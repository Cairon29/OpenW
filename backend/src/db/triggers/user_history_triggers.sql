-- Trigger: nombre
CREATE OR REPLACE FUNCTION trg_usuarios_name_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.name IS DISTINCT FROM NEW.name THEN
        INSERT INTO prev_user_name(fk_email_usuario, nombre_anterior, fecha_registro)
        VALUES (OLD.email, OLD.name, NOW() AT TIME ZONE 'UTC');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_usuarios_name ON usuarios;
CREATE TRIGGER trg_usuarios_name
BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION trg_usuarios_name_fn();

-- Trigger: telefono
CREATE OR REPLACE FUNCTION trg_usuarios_telefono_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.phone IS DISTINCT FROM NEW.phone THEN
        INSERT INTO prev_user_telefono(fk_email_usuario, telefono_anterior, fecha_registro)
        VALUES (OLD.email, OLD.phone, NOW() AT TIME ZONE 'UTC');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_usuarios_telefono ON usuarios;
CREATE TRIGGER trg_usuarios_telefono
BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION trg_usuarios_telefono_fn();

-- Trigger: vicepresidencia
CREATE OR REPLACE FUNCTION trg_usuarios_vicepresidencia_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.fk_id_vicepresidencia IS DISTINCT FROM NEW.fk_id_vicepresidencia THEN
        INSERT INTO prev_user_viceprecidencia(fk_email_usuario, fk_id_viceprecidencia, fecha_registro)
        VALUES (OLD.email, OLD.fk_id_vicepresidencia, NOW() AT TIME ZONE 'UTC');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_usuarios_vicepresidencia ON usuarios;
CREATE TRIGGER trg_usuarios_vicepresidencia
BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION trg_usuarios_vicepresidencia_fn();

-- Trigger: direccion
CREATE OR REPLACE FUNCTION trg_usuarios_direccion_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.fk_id_direccion IS DISTINCT FROM NEW.fk_id_direccion THEN
        INSERT INTO prev_user_direccion(fk_email_usuario, fk_id_direccion, fecha_registro)
        VALUES (OLD.email, OLD.fk_id_direccion, NOW() AT TIME ZONE 'UTC');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_usuarios_direccion ON usuarios;
CREATE TRIGGER trg_usuarios_direccion
BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION trg_usuarios_direccion_fn();
