"""
Authentication enums
"""

import enum

class UserRoleEnum(enum.Enum):
    """
    There are two main roles in regamsa operations, they have different purposes and permissions in the app workflow.
    Directives: They can see historic data, read them, analize metrics and dashboards, but cannot handle operations.
    Area Managers: They can see only historic data, metrics and handle operations, but for their area, not else more. 
    """
    DIRECTIVE = 'Directivo'
    AREA_MANAGER = 'Jefe de Área'
