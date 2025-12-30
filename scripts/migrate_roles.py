import sys
import os
import asyncio
from sqlalchemy import text

# Add backend directory to path so we can import 'app' BEFORE importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from app.models.role import Role

async def migrate_roles():
    async with engine.begin() as conn:
        # 1. Create roles table
        print("Creating roles table...")
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            label VARCHAR(100) NOT NULL,
            permissions JSON NOT NULL
        );
        """))

        # 2. Add role_id to employees if not exists
        try:
            await conn.execute(text("SELECT role_id FROM employees LIMIT 1"))
        except Exception:
            print("Adding role_id column to employees...")
            # MySQL syntax for adding column with FK
            await conn.execute(text("ALTER TABLE employees ADD COLUMN role_id INTEGER"))
            await conn.execute(text("ALTER TABLE employees ADD CONSTRAINT fk_employees_roles FOREIGN KEY (role_id) REFERENCES roles(id)"))

        # 3. Create default roles
        print("Creating default roles...")
        
        # Default Permissions
        read_only = {"create": False, "read": True, "update": False, "delete": False}
        full_access = {"create": True, "read": True, "update": True, "delete": True}
        no_access = {"create": False, "read": False, "update": False, "delete": False}

        admin_perms = {
            "dashboard": full_access, "inventory": full_access, "sales": full_access,
            "purchases_ruc10": full_access, "purchases_ruc20": full_access, "expenses": full_access,
            "payroll": full_access, "accounting": full_access, "settings": full_access
        }
        
        user_perms = {
            "dashboard": read_only, "inventory": read_only, "sales": full_access,
            "purchases_ruc10": no_access, "purchases_ruc20": no_access, "expenses": read_only,
            "payroll": no_access, "accounting": no_access, "settings": no_access
        }

        import json
        roles_to_insert = [
            ("ADMIN", "Administrador Principal", json.dumps(admin_perms)),
            ("USER", "Vendedor / Usuario", json.dumps(user_perms))
        ]

        for name, label, perms in roles_to_insert:
            res = await conn.execute(text(f"SELECT id FROM roles WHERE name = '{name}'"))
            role_id = res.scalar()
            
            if not role_id:
                await conn.execute(text(
                    "INSERT INTO roles (name, label, permissions) VALUES (:name, :label, :perms)"
                ), {"name": name, "label": label, "perms": perms})
                print(f"Created role: {name}")

        # 4. Migrate existing employees
        print("Migrating existing employees...")
        roles_res = await conn.execute(text("SELECT id, name FROM roles"))
        role_map = {row.name: row.id for row in roles_res}

        await conn.execute(text("UPDATE employees SET role_id = :admin_id WHERE role = 'ADMIN'"), {"admin_id": role_map.get('ADMIN', 1)})
        await conn.execute(text("UPDATE employees SET role_id = :user_id WHERE role = 'USER' OR role IS NULL"), {"user_id": role_map.get('USER', 2)})

    print("Migration completed.")

if __name__ == "__main__":
    asyncio.run(migrate_roles())
