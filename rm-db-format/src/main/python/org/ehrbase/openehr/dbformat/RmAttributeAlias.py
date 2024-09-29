from collections import defaultdict
from typing import List, Dict

class RmAttributeAlias:
    """For the database: Shorter aliases for attributes of RmObjects."""

    VALUES: List['RmAttributeAlias'] = [
        # INSTRUCTION
        # Short attribute names with aliases
        ('activities', 'a'),
        # COMPOSITION
        ('content', 'c'),
        ('context', 'x'),
        # ADMIN_ENTRY, EVALUATION, OBSERVATION, EVENT, INTERVAL_EVENT, POINT_EVENT
        ('data', 'd'),
        # ACTION, ACTIVITY
        ('description', 't'),
        # HISTORY
        ('events', 'e'),
        # ACTION
        ('instruction_details', 'n'),
        # ITEM_SINGLE
        ('item', 'j'),
        # SECTION, CLUSTER, ITEM_LIST, ITEM_TREE
        ('items', 'i'),
        # EVENT_CONTEXT
        ('other_context', 'o'),
        # ACTION, CARE_ENTRY, EVALUATION, INSTRUCTION, OBSERVATION
        ('protocol', 'p'),
        # ITEM_TABLE
        ('rows', 'r'),
        # OBSERVATION, EVENT, INTERVAL_EVENT, POINT_EVENT
        ('state', 's'),
        # HISTORY
        ('summary', 'y'),
        # INSTRUCTION_DETAILS
        ('wf_details', 'w'),
        # FEEDER_AUDIT
        ('feeder_audit', 'f'),
        ('accuracy', 'ay'),
        ('accuracy_is_percent', 'ayp'),
        ('action_archetype_id', 'aa'),
        ('activity_id', 'ac'),
        ('alternate_text', 'at'),
        ('archetype_details', 'ad'),
        ('archetype_id', 'aX'),
        ('archetype_node_id', 'A'),
        ('assigner', 'as'),
        ('attestations', 'att'),
        ('attested_view', 'atv'),
        ('careflow_step', 'cf'),
        ('category', 'ca'),
        ('change_type', 'ct'),
        ('charset', 'ch'),
        ('code_string', 'cd'),
        ('committer', 'co'),
        ('commit_audit', 'cau'),
        ('composer', 'cp'),
        ('compression_algorithm', 'calg'),
        ('contribution', 'con'),
        ('current_state', 'cu'),
        ('defining_code', 'df'),
        ('denominator', 'de'),
        ('details', 'dt'),
        ('domain_concept', 'dc'),
        ('duration', 'du'),
        ('encoding', 'ec'),
        ('end_time', 'et'),
        ('expiry_time', 'ex'),
        ('external_ref', 'er'),
        ('feeder_system_audit', 'fs'),
        ('feeder_system_item_ids', 'fX'),
        ('folders', 'fo'),
        ('formalism', 'fm'),
        ('formatting', 'fr'),
        ('function', 'fu'),
        ('guideline_id', 'gX'),
        ('health_care_facility', 'hc'),
        ('hyperlink', 'hy'),
        ('id', 'X'),
        ('identifiers', 'Xs'),
        ('instruction_id', 'iX'),
        ('integrity_check', 'ic'),
        ('integrity_check_algorithm', 'ica'),
        ('interval', 'in'),
        ('ism_transition', 'it'),
        ('issuer', 'is'),
        ('is_modifiable', 'im'),
        ('is_pending', 'ip'),
        ('is_queryable', 'iq'),
        ('is_terminal', 'il'),
        ('language', 'la'),
        ('lifecycle_state', 'ls'),
        ('links', 'lk'),
        ('location', 'lc'),
        ('lower', 'l'),
        ('lower_included', 'li'),
        ('lower_unbounded', 'lu'),
        ('magnitude', 'm'),
        ('magnitude_status', 'ms'),
        ('mappings', 'mp'),
        ('match', 'ma'),
        ('math_function', 'mf'),
        ('meaning', 'me'),
        ('media_type', 'mt'),
        ('mode', 'mo'),
        ('name', 'N'),
        ('namespace', 'ns'),
        ('narrative', 'nv'),
        ('normal_range', 'nr'),
        ('normal_status', 'nt'),
        ('null_flavour', 'nf'),
        ('null_reason', 'nl'),
        ('numerator', 'nu'),
        ('origin', 'og'),
        ('original_content', 'oc'),
        ('originating_system_audit', 'oa'),
        ('originating_system_item_ids', 'os'),
        ('other_details', 'od'),
        ('other_input_version_uids', 'oX'),
        ('other_participations', 'op'),
        ('other_reference_ranges', 'or'),
        ('participations', 'pp'),
        ('path', 'pa'),
        ('performer', 'pf'),
        ('period', 'pe'),
        ('preceding_version_uid', 'pX'),
        ('precision', 'pc'),
        ('preferred_term', 'pt'),
        ('proof', 'prf'),
        ('property', 'pr'),
        ('provider', 'pv'),
        ('purpose', 'pu'),
        ('qualified_rm_entity', 'qr'),
        ('range', 'ra'),
        ('reason', 're'),
        ('relationship', 'rs'),
        ('rm_entity', 'rm'),
        ('rm_name', 'rn'),
        ('rm_originator', 'ro'),
        ('rm_version', 'rv'),
        ('sample_count', 'sn'),
        ('scheme', 'sc'),
        ('setting', 'se'),
        ('signature', 'sig'),
        ('size', 'si'),
        ('specialisation', 'sp'),
        ('start_time', 'st'),
        ('subject', 'su'),
        ('symbol', 'sy'),
        ('system_id', 'sX'),
        ('target', 'ta'),
        ('template_id', 'tm'),
        ('terminology_id', 'te'),
        ('territory', 'ty'),
        ('thumbnail', 'th'),
        ('time', 'ti'),
        ('time_committed', 'tc'),
        ('timing', 'tg'),
        ('transition', 'tr'),
        ('type', 'tp'),
        ('uid', 'U'),
        ('units', 'un'),
        ('units_display_name', 'ud'),
        ('units_system', 'us'),
        ('upper', 'u'),
        ('upper_included', 'ui'),
        ('upper_unbounded', 'uu'),
        ('uri', 'ur'),
        ('value', 'V'),
        ('version_id', 'vX'),
        ('wf_definition', 'wd'),
        ('width', 'wi'),
        ('workflow_id', 'wX'),
        ('_index', 'I'),
        ('_magnitude', 'M'),
        (DbToRmFormat.TYPE_ATTRIBUTE, 'T')
    ]

    attribute2alias: Dict[str, str] = {}
    alias2attribute: Dict[str, str] = {}

    @classmethod
    def initialize(cls):
        cls.attribute2alias = {alias.attribute: alias.alias for alias in cls.VALUES}
        cls.alias2attribute = {alias.alias: alias.attribute for alias in cls.VALUES}

    @classmethod
    def get_alias(cls, attribute: str) -> str:
        alias = cls.attribute2alias.get(attribute)
        if alias is None:
            raise ValueError(f"Missing alias for attribute {attribute}")
        return alias

    @classmethod
    def rm_to_json_path_parts(cls, rm_path: str) -> List[str]:
        return [cls.get_alias(part) for part in rm_path.split("/")]

    @classmethod
    def get_attribute(cls, alias: str) -> str:
        attribute = cls.alias2attribute.get(alias)
        if attribute is None:
            raise ValueError(f"Missing attribute for alias {alias}")
        return attribute

# Initialize the mappings
RmAttributeAlias.initialize()
