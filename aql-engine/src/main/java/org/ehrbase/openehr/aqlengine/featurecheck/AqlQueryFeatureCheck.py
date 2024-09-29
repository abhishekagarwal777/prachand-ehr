from typing import List

class FeatureCheck:
    def __init__(self, system_service):
        self.system_service = system_service
    
    def ensure_supported(self, aql_query):
        raise NotImplementedError("Subclasses should implement this method.")

class FromCheck(FeatureCheck):
    # Implement specific checks
    pass

class SelectCheck(FeatureCheck):
    # Implement specific checks
    pass

class WhereCheck(FeatureCheck):
    # Implement specific checks
    pass

class OrderByCheck(FeatureCheck):
    # Implement specific checks
    pass

class AqlQuery:
    # Define this class based on actual requirements
    pass

class SystemService:
    # Define this class based on actual requirements
    pass

class AqlQueryFeatureCheck:
    def __init__(self, system_service: SystemService):
        self.feature_checks: List[FeatureCheck] = [
            FromCheck(system_service),
            SelectCheck(system_service),
            WhereCheck(system_service),
            OrderByCheck(system_service)
        ]

    def ensure_query_supported(self, aql_query: AqlQuery):
        for feature_check in self.feature_checks:
            feature_check.ensure_supported(aql_query)
