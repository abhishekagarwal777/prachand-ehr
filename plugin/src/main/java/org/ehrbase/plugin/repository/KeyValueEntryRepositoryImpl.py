from typing import List, Optional, Callable
from uuid import UUID
from jooq import DSLContext  # Adjust import based on your project structure
from spring import Component

from org.ehrbase.api.repository import KeyValuePair, KeyValuePairRepository
from org.ehrbase.jooq.pg.tables import Plugin  # Adjust import based on your project structure


@Component
class KeyValueEntryRepositoryImpl(KeyValuePairRepository):
    def __init__(self, ctx: DSLContext) -> None:
        self.ctx = ctx

    def find_all_by(self, context: str) -> List[KeyValuePair]:
        return [
            self.to_kvp(rec)
            for rec in self.ctx.fetch_stream(Plugin.PLUGIN, Plugin.PLUGIN.PLUGINID.eq(context))
        ]

    def find_by(self, context: str, key: str) -> Optional[KeyValuePair]:
        return (
            self.ctx.fetch_optional(Plugin.PLUGIN, Plugin.PLUGIN.PLUGINID.eq(context).and_(Plugin.PLUGIN.KEY.eq(key)))
            .map(self.to_kvp)
            .or_else(None)
        )

    def save(self, kve: KeyValuePair) -> KeyValuePair:
        rec = self.ctx.new_record(Plugin.PLUGIN)
        rec.set_id(kve.get_id())
        rec.set_pluginid(kve.get_context())
        rec.set_key(kve.get_key())
        rec.set_value(kve.get_value())

        rec.insert()
        return kve

    def find_by_uid(self, uid: UUID) -> Optional[KeyValuePair]:
        return (
            self.ctx.fetch_optional(Plugin.PLUGIN, Plugin.PLUGIN.ID.eq(uid))
            .map(self.to_kvp)
            .or_else(None)
        )

    def delete_by(self, uid: UUID) -> bool:
        res = self.ctx.delete(Plugin.PLUGIN).where(Plugin.PLUGIN.ID.eq(uid)).execute()
        return res > 0

    @staticmethod
    def to_kvp(rec) -> KeyValuePair:
        return KeyValuePair.of(rec.get_id(), rec.get_pluginid(), rec.get_key(), rec.get_value())
