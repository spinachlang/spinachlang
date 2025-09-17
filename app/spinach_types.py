""" "types used to describe the language structure"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from pytket import Qubit, Bit


class QubitDeclaration(BaseModel):
    """Association of a qubit number to a name"""

    name: str
    qubit: Qubit

    # pylint: disable=too-few-public-methods
    class Config:
        """class config"""

        arbitrary_types_allowed = True


class BitDeclaration(BaseModel):
    """Association of a qubit number to a name"""

    name: str
    bit: Bit

    # pylint: disable=too-few-public-methods
    class Config:
        """class config"""

        arbitrary_types_allowed = True


class ListDeclaration(BaseModel):
    """Association of a list to a name"""

    name: str
    items: List[str]


class GatePipeByName(BaseModel):
    """Call of a pipeline using its name"""

    name: str
    rev: bool


class GateCall(BaseModel):
    """Call of a gate with it's arguments"""

    name: str
    args: List[Union[str, int]] = Field(default_factory=list)


class GatePipeline(BaseModel):
    """The representation of a pipeline"""

    parts: List[Union[GateCall, GatePipeByName]]


class InstructionDeclaration(BaseModel):
    """Association of a gate pipe to a name"""

    name: str
    pipeline: GatePipeline


class Action(BaseModel):
    """Execution of a gatepipe on a qubit"""

    target: Union[str, int, list]
    count: Optional[int] = None
    instruction: Union[GatePipeline, str]
