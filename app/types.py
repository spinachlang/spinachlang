from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Union


class QubitDeclaration(BaseModel):
    name: str
    number: int


class ListDeclaration(BaseModel):
    name: str
    items: List[str]


class GateCall(BaseModel):
    name: str
    args: List[Union[str, int]] = Field(default_factory=list)


class GatePipeline(BaseModel):
    parts: List[Union[GateCall, str]]


class InstructionDeclaration(BaseModel):
    name: str
    pipeline: GatePipeline


class Action(BaseModel):
    target: str
    index: Optional[int] = None
    operation: Union[GatePipeline, str]
