from . import models, database
from sqlalchemy import text

def fix():
    print("🔄 Verificando base de datos...")
    
    # 1. Force Create Tables
    try:
        models.Base.metadata.create_all(bind=database.engine)
        print("✅ Tablas sincronizadas (create_all ejecutado).")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return

    # 2. Check Categories
    db = database.SessionLocal()
    try:
        cats = db.query(models.Category).all()
        print(f"📊 Categorías encontradas: {len(cats)}")
        for c in cats:
            print(f"   - {c.id}: {c.name}")
        
        if len(cats) == 0:
            print("⚠️ No hay categorías. CREANDO DEFAULTS AHORA...")
            defaults = ['Alimentación', 'Transporte', 'Vivienda', 'Entretenimiento', 'Salud', 'Educación', 'Servicios', 'Otros']
            for name in defaults:
                try:
                    db.add(models.Category(name=name))
                except:
                    pass
            db.commit()
            print("✅ Categorías por defecto creadas.")
            
    except Exception as e:
        print(f"❌ Error consultando categorías: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix()
