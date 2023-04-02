from config import AISConfig
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(AISConfig.URL, echo=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)
