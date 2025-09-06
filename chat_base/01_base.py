from pydantic import BaseModel, Field


class Folly(BaseModel):
    a: str = Field(default="default A", description="first arg")
    b: str = Field(default="default B", description="second arg")
    


c = Folly()
print(c)
d = Folly(a="hello", b="world")
print(d)
