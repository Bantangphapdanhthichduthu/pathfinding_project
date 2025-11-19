from sqlalchemy import Column, String, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class NodeModel(Base):
    __tablename__ = "nodes"
    
    name = Column(String, primary_key=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    
    # Relationships
    edges_from = relationship("EdgeModel", foreign_keys="EdgeModel.node_from", back_populates="source")
    edges_to = relationship("EdgeModel", foreign_keys="EdgeModel.node_to", back_populates="target")
    
    def __repr__(self):
        return f"<Node(name={self.name}, x={self.x}, y={self.y})>"


class EdgeModel(Base):
    __tablename__ = "edges"
    
    node_from = Column(String, ForeignKey("nodes.name"), nullable=False)
    node_to = Column(String, ForeignKey("nodes.name"), nullable=False)
    weight = Column(Float, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('node_from', 'node_to'),
    )
    
    # Relationships
    source = relationship("NodeModel", foreign_keys=[node_from], back_populates="edges_from")
    target = relationship("NodeModel", foreign_keys=[node_to], back_populates="edges_to")
    
    def __repr__(self):
        return f"<Edge(from={self.node_from}, to={self.node_to}, weight={self.weight})>"