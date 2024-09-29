class EHRbaseHeader:
    """EHRbase specific HTTP headers that are not part of the openEHR standard."""
    
    TEMPLATE_ID = "EHRBase-Template-ID"
    
    AQL_DRY_RUN = "EHRbase-AQL-Dry-Run"
    
    AQL_EXECUTED_SQL = "EHRbase-AQL-Executed-SQL"
    
    AQL_QUERY_PLAN = "EHRbase-AQL-Query-Plan"
