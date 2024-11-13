import inspect

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from .artefacts import BaseArtefact, Artefactory


class InterruptPipeline(Exception):
    pass


class ChainingError(Exception):
    def __init__(self, needs: BaseArtefact):
        super().__init__(f'Artefact {needs} is needed but not produced by predecessor')


@dataclass
class Pipeline:
    artefactory: Artefactory
    steps: list['Step'] = field(default_factory=list)
    expects: list[BaseArtefact] = field(default_factory=list)
    
    def process(self, *args: tuple[BaseArtefact, object], no_except: bool=False) -> Artefactory:
        for key, value in args:
            self.artefactory[key] = value
        
        try:
            for step in self.steps:            
                step.process(self.artefactory)
            return self.artefactory
        except InterruptPipeline as e:
            if no_except:
                raise e
        
    @property
    def _signature(self) -> tuple[set[BaseArtefact], set[BaseArtefact]]:
        needs, produces = set(), set()
        for step in self.steps:
            for need in step.needs:
                if need not in produces:
                    needs.add(need)
            for produce in step.produces:
                produces.add(produce)
        return needs, produces
                
    
    def __add__(self, other: 'Step' | 'Pipeline') -> 'Pipeline':
        needs, produces = self._signature
        if isinstance(other, Step):
            for need in other.needs:
                if need not in produces and need not in needs: #  Assuming "entry point" artefacts
                    raise ChainingError(need)
            return Pipeline(*self.steps, other)
        if isinstance(other, Pipeline):
            for need in other._signature[0]:
                if need not in produces:
                    raise ChainingError(need)
            return Pipeline(*(self.steps + other))
        
        raise ValueError('Not a valid pipeline chaining type')
    
    # A destructive action, should not be used on a pipeline that's meant to be used as a separate entity
    def as_step(owner) -> 'Step':
        class PipelineStep(Step):
            def __init__(self, needs, produces):
                super().__init__(needs, produces)
            
            def process(self, artefactory):
                owner.artefactory = artefactory
                owner.process(no_except=True)
                
        needs, produces = owner._signature
        return PipelineStep(list(needs), list(produces))


class Step(ABC):
    _KEYWORDS = ('self', 'artefactory')
    
    def __init__(self, needs: list[BaseArtefact], produces: list[BaseArtefact]):
        self.needs = needs
        self.produces = produces
        
    @staticmethod
    def resolve_artefacts(**mapping: BaseArtefact):
        def decorator(fn: Callable):
            spec = inspect.getfullargspec(fn)
            params = {*spec.args, *spec.kwonlyargs}
            
            def wrapper(self, artefactory: Artefactory):
                kwargs = {key: artefactory[mapping[key]] for key in params if key not in Step._KEYWORDS}
                return fn(self, artefactory, **kwargs)
            
            return wrapper
        
        return decorator
        
    @abstractmethod
    def process(self, a: Artefactory, *args, **kwargs):
        pass
