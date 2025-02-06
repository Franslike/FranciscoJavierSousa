from datetime import datetime, timedelta
from typing import List, Dict, Optional
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG

class NotificationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def obtener_notificaciones_usuario(self, id_usuario: int, solo_no_leidas: bool = False) -> List[Dict]:
        """Obtener las notificaciones de un usuario específico"""
        query = """
        SELECT id_notificacion, tipo, mensaje, fecha_generacion, estado, 
               entidad_id, entidad_tipo
        FROM notificaciones 
        WHERE id_usuario = %s
        """
        
        if solo_no_leidas:
            query += " AND estado = 'no_leida'"
            
        query += " ORDER BY fecha_generacion DESC"
        
        try:
            notificaciones = self.db_manager.ejecutar_query(query, (id_usuario,), dictionary=True)
            return notificaciones if notificaciones else []
        except Exception as e:
            print(f"Error al obtener notificaciones: {e}")
            return []

    def contar_notificaciones_no_leidas(self, id_usuario: int) -> int:
        """Contar el número de notificaciones no leídas para un usuario"""
        query = """
        SELECT COUNT(*) as count 
        FROM notificaciones 
        WHERE id_usuario = %s AND estado = 'no_leida'
        """
        try:
            result = self.db_manager.ejecutar_query(query, (id_usuario,), fetchone=True)
            return result[0] if result else 0
        except Exception as e:
            print(f"Error al contar notificaciones: {e}")
            return 0

    def marcar_como_leida(self, id_notificacion: int) -> bool:
        """Marcar una notificación específica como leída"""
        query = """
        UPDATE notificaciones 
        SET estado = 'leida' 
        WHERE id_notificacion = %s
        """
        try:
            self.db_manager.ejecutar_query(query, (id_notificacion,), commit=True)
            return True
        except Exception as e:
            print(f"Error al marcar notificación como leída: {e}")
            return False

    def marcar_todas_como_leidas(self, id_usuario: int) -> bool:
        """Marcar todas las notificaciones de un usuario como leídas"""
        query = """
        UPDATE notificaciones 
        SET estado = 'leida' 
        WHERE id_usuario = %s AND estado = 'no_leida'
        """
        try:
            self.db_manager.ejecutar_query(query, (id_usuario,), commit=True)
            return True
        except Exception as e:
            print(f"Error al marcar todas las notificaciones como leídas: {e}")
            return False

    def crear_notificacion(self, id_usuario: int, tipo: str, mensaje: str, 
                         entidad_id: Optional[int] = None, 
                         entidad_tipo: Optional[str] = None) -> bool:
        """Crear una nueva notificación"""
        query = """
        INSERT INTO notificaciones 
        (id_usuario, tipo, mensaje, entidad_id, entidad_tipo)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.db_manager.ejecutar_query(
                query, 
                (id_usuario, tipo, mensaje, entidad_id, entidad_tipo),
                commit=True
            )
            return True
        except Exception as e:
            print(f"Error al crear notificación: {e}")
            return False

    def verificar_periodos_por_vencer(self) -> List[Dict]:
        """Verificar períodos que están próximos a vencer (3 días o menos)"""
        query = """
        SELECT p.id_periodo, p.fecha_fin, p.tipo,
            DATEDIFF(p.fecha_fin, CURDATE()) as dias_restantes
        FROM periodos_nomina p
        WHERE p.estado = 'abierto' 
        AND DATEDIFF(p.fecha_fin, CURDATE()) BETWEEN 0 AND 3
        AND NOT EXISTS (
            SELECT 1 FROM notificaciones n 
            WHERE n.entidad_id = p.id_periodo 
            AND n.tipo = 'periodo'
            AND n.estado IN ('leida', 'no_leida')
            AND DATE(n.fecha_generacion) = CURDATE()
        )
        """
        try:
            return self.db_manager.ejecutar_query(query, dictionary=True)
        except Exception as e:
            print(f"Error al verificar períodos: {e}")
            return []

    def verificar_prestamos_liquidados(self) -> List[Dict]:
        """Verificar préstamos liquidados sin notificación previa"""
        query = """
        SELECT p.id_prestamo, p.id_empleado, 
            CONCAT(e.nombre, ' ', e.apellido) as empleado
        FROM prestamos p
        JOIN empleados e ON p.id_empleado = e.id_empleado
        WHERE p.estado = 'liquidado'
        AND NOT EXISTS (
            SELECT 1 FROM notificaciones n 
            WHERE n.entidad_id = p.id_prestamo 
            AND n.tipo = 'prestamo'
            AND n.estado IN ('leida', 'no_leida')
        )
        """
        try:
            return self.db_manager.ejecutar_query(query, dictionary=True)
        except Exception as e:
            print(f"Error al verificar préstamos liquidados: {e}")
            return []
        
    def notificar_cambio_estado_prestamo(self, prestamo_id: int, nuevo_estado: str, 
                                    empleado_nombre: str, motivo: str = None):
        """Notificar al empleado sobre cambios en el estado de su préstamo"""
        try:
            # Obtener id_usuario del empleado
            query = """
            SELECT u.id_usuario
            FROM usuarios u
            JOIN empleados e ON u.id_empleado = e.id_empleado
            JOIN prestamos p ON e.id_empleado = p.id_empleado
            WHERE p.id_prestamo = %s
            """
            result = self.db_manager.ejecutar_query(query, (prestamo_id,), fetchone=True)
            if result:
                id_usuario = result[0]
                mensaje = f"Su solicitud de préstamo ha sido {nuevo_estado}"
                if motivo:
                    mensaje += f"\nMotivo: {motivo}"
                
                self.crear_notificacion(
                    id_usuario,
                    'prestamo',
                    mensaje,
                    prestamo_id,
                    'prestamo'
                )
                
        except Exception as e:
            print(f"Error al notificar cambio de estado: {e}")

    def verificar_inasistencias(self) -> List[Dict]:
        """Verificar inasistencias después de las 8:30 AM"""
        query = """
        SELECT e.id_empleado, 
            CONCAT(e.nombre, ' ', e.apellido) as empleado,
            1 as inasistencias
        FROM empleados e
        WHERE e.status = 'activo'
        AND NOT EXISTS (
            SELECT 1 
            FROM asistencias a 
            WHERE a.id_empleado = e.id_empleado 
            AND DATE(a.entrada) = CURDATE()
        )
        AND NOT EXISTS (
            SELECT 1
            FROM justificativos j
            WHERE j.id_empleado = e.id_empleado
            AND j.fecha = CURDATE()
        )
        AND TIME(NOW()) > '08:30:00'
        """
        try:
            return self.db_manager.ejecutar_query(query, dictionary=True)
        except Exception as e:
            print(f"Error al verificar inasistencias: {e}")
            return []

    def eliminar_notificaciones_antiguas(self, dias: int = 30) -> bool:
        """Eliminar notificaciones más antiguas que el número de días especificado"""
        query = """
        DELETE FROM notificaciones 
        WHERE fecha_generacion < DATE_SUB(NOW(), INTERVAL %s DAY)
        AND estado = 'leida'
        """
        try:
            self.db_manager.ejecutar_query(query, (dias,), commit=True)
            return True
        except Exception as e:
            print(f"Error al eliminar notificaciones antiguas: {e}")
            return False
        
    def obtener_usuarios_para_notificar(self, tipo_permiso: str) -> List[Dict]:
        """Obtener lista de usuarios que deben recibir notificaciones según el tipo"""
        query = """
        SELECT DISTINCT u.id_usuario
        FROM usuarios u
        WHERE u.estado = 'activo'
        AND (
            u.rol IN ('admin', 'gerente')
            OR EXISTS (
                SELECT 1 FROM usuario_permisos up
                JOIN permisos_sistema ps ON up.id_permiso = ps.id_permiso
                WHERE up.id_usuario = u.id_usuario
                AND ps.codigo LIKE %s
            )
        )
        """
        try:
            return self.db_manager.ejecutar_query(query, (f"{tipo_permiso}%",))
        except Exception as e:
            print(f"Error al obtener usuarios para notificar: {e}")
            return []

    def verificar_y_crear_notificaciones(self, trigger_user_id: int = None):
        """
        Verificar y crear notificaciones para todos los usuarios correspondientes
        Args:
            trigger_user_id: ID del usuario que triggereó la verificación (opcional)
        """
        # Verificar períodos por vencer
        periodos = self.verificar_periodos_por_vencer()
        if periodos:
            usuarios = self.obtener_usuarios_para_notificar('periodos')
            for periodo in periodos:
                for usuario in usuarios:
                    id_usuario = usuario[0]
                    # Verificar si ya existe notificación
                    query = """
                    SELECT 1 FROM notificaciones 
                    WHERE entidad_id = %s 
                    AND tipo = 'periodo'
                    AND id_usuario = %s
                    AND estado IN ('leida', 'no_leida')
                    AND DATE(fecha_generacion) = CURDATE()
                    """
                    existe = self.db_manager.ejecutar_query(query, 
                        (periodo['id_periodo'], id_usuario), 
                        fetchone=True
                    )
                    
                    if not existe:
                        mensaje = f"El período {periodo['tipo']} vence en {periodo['dias_restantes']} días"
                        self.crear_notificacion(
                            id_usuario, 
                            'periodo', 
                            mensaje,
                            periodo['id_periodo'],
                            'periodo'
                        )

        # Verificar préstamos liquidados
        prestamos = self.verificar_prestamos_liquidados()
        if prestamos:
            usuarios = self.obtener_usuarios_para_notificar('prestamos')
            for prestamo in prestamos:
                for usuario in usuarios:
                    id_usuario = usuario[0]
                    # Verificar si ya existe notificación
                    query = """
                    SELECT 1 FROM notificaciones 
                    WHERE entidad_id = %s 
                    AND tipo = 'prestamo'
                    AND id_usuario = %s
                    AND estado IN ('leida', 'no_leida')
                    AND DATE(fecha_generacion) = CURDATE()
                    """
                    existe = self.db_manager.ejecutar_query(query,
                        (prestamo['id_prestamo'], id_usuario),
                        fetchone=True
                    )
                    
                    if not existe:
                        mensaje = f"El préstamo del empleado {prestamo['empleado']} ha sido liquidado"
                        self.crear_notificacion(
                            id_usuario,
                            'prestamo',
                            mensaje,
                            prestamo['id_prestamo'],
                            'prestamo'
                        )

        # Verificar inasistencias
        inasistencias = self.verificar_inasistencias()
        if inasistencias:
            usuarios = self.obtener_usuarios_para_notificar('asistencias')
            for inasistencia in inasistencias:
                for usuario in usuarios:
                    id_usuario = usuario[0]
                    # Verificar si ya existe notificación
                    query = """
                    SELECT 1 FROM notificaciones 
                    WHERE entidad_id = %s 
                    AND tipo = 'inasistencia'
                    AND id_usuario = %s
                    AND estado IN ('leida', 'no_leida')
                    AND DATE(fecha_generacion) = CURDATE()
                    """
                    existe = self.db_manager.ejecutar_query(query,
                        (inasistencia['id_empleado'], id_usuario),
                        fetchone=True
                    )
                    
                    if not existe:
                        mensaje = f"El empleado {inasistencia['empleado']} registra {inasistencia['inasistencias']} inasistencias"
                        self.crear_notificacion(
                            id_usuario,
                            'inasistencia',
                            mensaje,
                            inasistencia['id_empleado'],
                            'empleado'
                        )