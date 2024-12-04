import re
from typing import List, Optional
import logging
from datetime import datetime
from croniter import croniter

class CronTranslator:
    """
    Traductor de expresiones cron al español 
    con implementación simplificada.
    """
    
    _MONTH_NAMES = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    
    _DAY_NAMES = [
        'domingo', 'lunes', 'martes', 'miércoles', 
        'jueves', 'viernes', 'sábado'
    ]
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Inicializa el traductor con configuraciones básicas.
        
        :param log_level: Nivel de logging
        """
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _validate_cron_expression(self, expression: str) -> bool:
        """
        Valida la sintaxis de la expresión cron.
        
        :param expression: Expresión cron a validar
        :return: Booleano indicando si la expresión es válida
        """
        try:
            croniter(expression)
            return True
        except (ValueError, TypeError):
            return False
    
    def _parse_field(
        self, 
        value: str, 
        type_name: str, 
        names_list: Optional[List[str]] = None
    ) -> str:
        """
        Parsea campos individuales de una expresión cron.
        
        :param value: Valor del campo
        :param type_name: Tipo de campo (minuto, hora, etc)
        :param names_list: Lista opcional de nombres para mapeo
        :return: Descripción traducida del campo
        """
        if value == '*':
            return f'cada {type_name}'
        
        # Manejar conjuntos de valores
        if ',' in value:
            valores = value.split(',')
            if names_list:
                return f'los {", ".join(names_list[int(v)] for v in valores if int(v) < len(names_list))}'
            return f'{type_name}s: {", ".join(valores)}'
        
        # Manejar rangos
        if '-' in value:
            inicio, fin = map(int, value.split('-'))
            if names_list:
                return f'de {names_list[inicio]} a {names_list[fin]}'
            return f'{type_name}s del {inicio} al {fin}'
        
        # Manejar intervalos
        if '/' in value:
            _, intervalo = value.split('/')
            return f'cada {intervalo} {type_name}s'
        
        return value
    
    def translate(self, cron_expression: str) -> str:
        """
        Traduce una expresión cron completa a español.
        
        :param cron_expression: Expresión cron estándar
        :return: Descripción en español de la ejecución
        """
        if not self._validate_cron_expression(cron_expression):
            raise ValueError(f"Expresión cron inválida: {cron_expression}")
        
        try:
            minute, hour, day_of_month, month, day_of_week = cron_expression.split()
        except ValueError:
            raise ValueError("Formato de expresión cron inválido.")
        
        translations = []
        
        # Minutos
        translations.append(self._parse_field(minute, 'minuto'))
        
        # Horas
        translations.append(self._parse_field(hour, 'hora'))
        
        # Días del mes
        translations.append(self._parse_field(day_of_month, 'día del mes'))
        
        # Meses
        translations.append(self._parse_field(month, 'mes', self._MONTH_NAMES))
        
        # Días de la semana
        translations.append(self._parse_field(day_of_week, 'día', self._DAY_NAMES))
        
        return ' '.join(translations)
    
    def get_next_executions(self, cron_expression: str, count: int = 5) -> List[datetime]:
        """
        Calcula las próximas ejecuciones de una expresión cron.
        
        :param cron_expression: Expresión cron
        :param count: Número de próximas ejecuciones
        :return: Lista de próximas fechas de ejecución
        """
        try:
            base = datetime.now()
            cron = croniter(cron_expression, base)
            return [cron.get_next(datetime) for _ in range(count)]
        except Exception as e:
            self.logger.error(f"Error calculando próximas ejecuciones: {e}")
            return []

def main():
    """Función de demostración"""
    translator = CronTranslator()
    
    cron_expressions = [
        '*/5 * * * *',           # Cada 5 minutos
        '0 2 * * 1-5',            # 2 AM en días laborables
        '0 0 1 */2 *',            # Primer día de cada dos meses
        '30 3 15 * *',            # Día 15 de cada mes a las 3:30 AM
        '0 12 * * 1,3,5',         # Mediodía en lunes, miércoles y viernes
    ]
    
    for expression in cron_expressions:
        try:
            print(f"\nExpresión: {expression}")
            print("Traducción:", translator.translate(expression))
            print("Próximas ejecuciones:")
            for exec_time in translator.get_next_executions(expression):
                print(f"  - {exec_time}")
        except Exception as e:
            print(f"Error procesando {expression}: {e}")

if __name__ == "__main__":
    main()