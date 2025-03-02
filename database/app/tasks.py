import asyncio
import logging
from typing import List, Dict, Any
from celery import shared_task, group
from celery.result import GroupResult
try:
    from .celery_app import celery_app
    from .helper.pinecone import db_helper_obj
except ImportError:
    from celery_app import celery_app
    from helper.pinecone import db_helper_obj

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Maximum number of vectors per Pinecone upsert
MAX_BATCH_SIZE = 1000

@shared_task(name="app.tasks.upsert_batch")
def upsert_batch(vector_batch: List[Dict[str, Any]], index_name: str = "decision-agent", namespace: str = "ns1") -> Dict:
    """
    Process a batch of vectors (up to 1000) and upsert them to Pinecone.
    
    Args:
        vector_batch: List of vector dictionaries with 'embedding' and 'sentence'
        index_name: Pinecone index name
        namespace: Pinecone namespace
    
    Returns:
        Dict with status and results
    """
    try:
        logger.info(f"Processing batch of {len(vector_batch)} vectors")
        
        # Run the async upsert in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            db_helper_obj.upsert_method(vector_batch, index_name, namespace)
        )
        loop.close()
        
        logger.info(f"Successfully upserted batch: {result}")
        return {
            "status": "success",
            "vectors_processed": len(vector_batch),
            "result": result
        }
    except Exception as e:
        logger.error(f"Error upserting batch: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@shared_task(name="app.tasks.track_upsert_group")
def track_upsert_group(task_ids: List[str]) -> Dict:
    """
    Track the status of multiple batch tasks and return a summary.
    
    Args:
        task_ids: List of task IDs to track
        
    Returns:
        Dict with overall status and summary of all tasks
    """
    try:
        logger.info(f"Tracking group of {len(task_ids)} tasks")
        
        # Check status of all tasks
        results = []
        completed = 0
        failed = 0
        
        for task_id in task_ids:
            result = celery_app.AsyncResult(task_id)
            status = result.status
            
            if status == 'SUCCESS':
                completed += 1
                task_result = result.result
            elif status == 'FAILURE':
                failed += 1
                task_result = str(result.result)
            else:
                task_result = None
                
            results.append({
                "task_id": task_id,
                "status": status,
                "result": task_result
            })
        
        # Calculate overall status
        if failed > 0:
            overall_status = "partial_failure" if completed > 0 else "failure"
        elif completed == len(task_ids):
            overall_status = "success"
        else:
            overall_status = "in_progress"
            
        logger.info(f"Group status: {overall_status} ({completed}/{len(task_ids)} completed, {failed} failed)")
        
        return {
            "status": overall_status,
            "total_tasks": len(task_ids),
            "completed": completed,
            "failed": failed,
            "task_results": results
        }
    except Exception as e:
        logger.error(f"Error tracking task group: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@shared_task(name="app.tasks.process_large_upsert")
def process_large_upsert(vectors: List[Dict[str, Any]], index_name: str = "decision-agent", namespace: str = "ns1") -> Dict:
    """
    Split a large list of vectors into batches and process them using Celery tasks.
    
    Args:
        vectors: List of vector dictionaries with 'embedding' and 'sentence'
        index_name: Pinecone index name
        namespace: Pinecone namespace
    
    Returns:
        Dict with status and task IDs
    """
    try:
        total_vectors = len(vectors)
        logger.info(f"Processing large upsert with {total_vectors} vectors")
        
        # Split vectors into batches of MAX_BATCH_SIZE
        batches = [vectors[i:i + MAX_BATCH_SIZE] for i in range(0, total_vectors, MAX_BATCH_SIZE)]
        
        # Create a task for each batch
        task_ids = []
        for batch in batches:
            task = upsert_batch.delay(batch, index_name, namespace)
            task_ids.append(task.id)
        
        # Create a tracking task for the group
        track_task = track_upsert_group.delay(task_ids)
        
        logger.info(f"Created {len(task_ids)} batch tasks with tracking task {track_task.id}")
        return {
            "status": "success",
            "total_vectors": total_vectors,
            "batch_count": len(batches),
            "task_ids": task_ids,
            "tracking_task_id": track_task.id
        }
    except Exception as e:
        logger.error(f"Error processing large upsert: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        } 