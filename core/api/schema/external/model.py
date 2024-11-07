from sqlalchemy import Column, String, DateTime, func, ForeignKey, Boolean, Text, ARRAY, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from api.db import Base

class ExternalRepoModel(Base):
    __tablename__ = 'external_repo'

    id = Column(String, primary_key=True, nullable=False)
    insert_datetime = Column(DateTime)
    update_datetime = Column(DateTime)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)
    dataType = Column(String, nullable=False)
    deletedDate = Column(Integer)
    permanentlyDeletedAt = Column(Integer)
    isStarred = Column(Boolean, nullable=False)
    starredFields = Column(ARRAY(String))
    ingestBlock = Column(DateTime)
    usageTag = Column(String)
    uncompressedByteSize = Column(Integer, nullable=False)
    compressedByteSize = Column(Integer, nullable=False)
    uncompressedByteSizeOfMerged = Column(Integer)
    compressedByteSizeOfMerged = Column(Integer)
    timeOfLatestIngest = Column(DateTime)
    timeBasedRetention = Column(Float)
    ingestSizeBasedRetention = Column(Float)
    storageSizeBasedRetention = Column(Float)
    timeBasedBackupRetention = Column(Float)
    maxAutoShardCount = Column(Integer)
    automaticSearch = Column(Boolean, nullable=False)
    viewerQueryPrefix = Column(Text)
    tags = Column(ARRAY(String))

class ExternalViewModel(Base):
    __tablename__ = 'external_view'

    id = Column(String, primary_key=True, nullable=False)
    insert_datetime = Column(DateTime)
    update_datetime = Column(DateTime)
    name = Column(String, nullable=False)
    description = Column(Text)
    deletedDate = Column(Integer)
    permanentlyDeletedAt = Column(Integer)
    isStarred = Column(Boolean, nullable=False)
    automaticSearch = Column(Boolean, nullable=False)
    viewerQueryPrefix = Column(Text)
    tags = Column(ARRAY(String), nullable=False)
    starredFields = Column(ARRAY(String), nullable=False)

class ExternalAlertModel(Base):
    __tablename__ = 'external_alert'

    id = Column(String, primary_key=True, nullable=False)
    insert_datetime = Column(DateTime)
    update_datetime = Column(DateTime)
    ext_repo_id = Column(String)
    ext_view_id = Column(String)
    enabled = Column(Boolean)
    displayName = Column(String)
    description = Column(String)
    queryString = Column(Text)
    queryStart = Column(String)
    throttleTimeMillis = Column(Integer)
    throttleField = Column(String)
    timeOfLastTrigger = Column(DateTime)
    actions = Column(ARRAY(String))
    lastError = Column(String)
    labels = Column(ARRAY(String))
    yamlTemplate = Column(Text)
    packageId = Column(String)
    assetType = Column(String)
    queryString_hash = Column(String)

class ExternalFieldModel(Base):
    __tablename__ = 'external_field'

    ext_alert_id = Column(String, primary_key=True, nullable=False)
    insert_datetime = Column(DateTime)
    update_datetime = Column(DateTime)
    value = Column(String, nullable=False)

class ExternalActionModel(Base):
    __tablename__ = 'external_action'

    ext_alert_id = Column(String, primary_key=True, nullable=False)
    insert_datetime = Column(DateTime)
    update_datetime = Column(DateTime)
    id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    displayName = Column(String)
    yamlTemplate = Column(Text)
    isAllowedToRun = Column(Boolean, nullable=False)
    packageId = Column(String)
    yamlTemplate_hash = Column(String)
