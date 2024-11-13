from abc import ABC, abstractmethod
from dataclasses import dataclass


_ITEM_SUFFIX = '__item'


@dataclass
class BaseArtefact(ABC):
    key: str
    value_type: type
    
    def is_collection_item(self) -> bool:
        return self.key.endswith(_ITEM_SUFFIX)
    
    @property
    def parent_collection_key(self) -> str:
        if not self.is_collection_item():
            raise MissingArtefactError()
        return self.key.removesuffix(_ITEM_SUFFIX)
    
    @abstractmethod
    def check_type(self, item: object) -> bool:
        pass
    
    
class ArtefactError(Exception):
    def __init__(self, artefact: BaseArtefact, *args):
        super().__init__(artefact, *args)
        self.artefact = artefact
    

class MissingArtefactError(ArtefactError):
    def __init__(self, artefact: BaseArtefact, details: str):
        super().__init__(artefact, details)
        

class UnsupportedArtefactError(ArtefactError):
    def __init__(self, artefact: BaseArtefact):
        super().__init__(artefact, f'Artefact {artefact.key} is not expected to appear in this artefactory')
        

class WrongArtefactTypeError(ArtefactError):
    def __init__(self, artefact: BaseArtefact, value):
        super().__init__(artefact, f'Artefact {artefact.key} of type {artefact.value_type} is assigned value {value} of type {type(value)}')


@dataclass(unsafe_hash=True, frozen=True)
class Artefact(BaseArtefact):
    def check_type(self, item: object):
        return isinstance(item, self.value_type)


@dataclass(unsafe_hash=True, frozen=True)
class ArtefactCollection(BaseArtefact):
    group: str | None = None
    
    def check_type(self, item: object):
        if not isinstance(item, list):
            return False
        for subitem in item:
            if not isinstance(subitem, self.value_type):
                return False
        return True
    
    @property
    def item(self):
        return Artefact(f'{self.key}{_ITEM_SUFFIX}', self.value_type)
    

class Artefactory:
    def __init__(self, artefacts: list[BaseArtefact]):
        self.keys = set(artefacts)
        self.artefacts: dict[str, object] = {}
        
    def __getitem__(self, key: BaseArtefact) -> object:
        value = self.artefacts.get(key.key)
        if value is None:
            raise MissingArtefactError(key, 'no such artefact')
        return value
    
    def __setitem__(self, key: BaseArtefact, value: object):
        if key not in self.keys:
            raise UnsupportedArtefactError(key)
        if not key.check_type(value):
            raise WrongArtefactTypeError(key, value)
        self.artefacts[key.key] = value
        
    def indexer(owner, group: str) -> 'Artefactory':
        collection_keys = {
            collection.key: collection 
            for collection in owner.keys
            if isinstance(collection, ArtefactCollection) and collection.group == group
        }
        
        class IndexArtefactory(Artefactory):
            def __init__(self, index: int):
                self.index = index
            
            def __getitem__(self, key: BaseArtefact):
                if not key.is_collection_item() or key.parent_collection_key not in collection_keys:
                    return owner[key]
                
                value = owner[key]
                if self.index >= len(value):
                    raise MissingArtefactError(key, f'no index {self.index} for this artefact')
                return self.index, value[self.index]
            
            def __setitem__(self, key: BaseArtefact, value: object):
                if not key.is_collection_item() or key.parent_collection_key not in collection_keys:
                    owner[key] = value
                    return
                if not key.check_type(value):
                    raise WrongArtefactTypeError(key, value)
                
                collection = collection_keys[key.parent_collection_key]
                items = owner[collection]
                while len(items) <= self.index:
                    items.append(None)
                items[self.index] = value
                
        return IndexArtefactory()