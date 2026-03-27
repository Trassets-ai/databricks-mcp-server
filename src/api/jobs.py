"""
API for managing Databricks jobs.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def create_job(job_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Databricks job.
    
    Args:
        job_config: Job configuration
        
    Returns:
        Response containing the job ID
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Creating new job")
    return make_api_request("POST", "/api/2.0/jobs/create", data=job_config)


async def run_job(
    job_id: int,
    notebook_params: Optional[Dict[str, Any]] = None,
    python_params: Optional[List[str]] = None,
    jar_params: Optional[List[str]] = None,
    spark_submit_params: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run a job now.

    Args:
        job_id: ID of the job to run
        notebook_params: Optional parameters for notebook tasks
        python_params: Optional parameters for Python tasks (list of strings)
        jar_params: Optional parameters for JAR tasks (list of strings)
        spark_submit_params: Optional parameters for Spark submit tasks (list of strings)

    Returns:
        Response containing the run ID

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Running job: {job_id}")

    run_params: Dict[str, Any] = {"job_id": job_id}
    if notebook_params:
        run_params["notebook_params"] = notebook_params
    if python_params is not None:
        run_params["python_params"] = python_params
    if jar_params is not None:
        run_params["jar_params"] = jar_params
    if spark_submit_params is not None:
        run_params["spark_submit_params"] = spark_submit_params

    return make_api_request("POST", "/api/2.0/jobs/run-now", data=run_params)


async def list_jobs() -> Dict[str, Any]:
    """
    List all jobs.
    
    Returns:
        Response containing a list of jobs
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Listing all jobs")
    return make_api_request("GET", "/api/2.0/jobs/list")


async def get_job(job_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Response containing job information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for job: {job_id}")
    return make_api_request("GET", "/api/2.0/jobs/get", params={"job_id": job_id})


async def update_job(job_id: int, new_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing job.
    
    Args:
        job_id: ID of the job to update
        new_settings: New job settings
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Updating job: {job_id}")
    
    update_data = {
        "job_id": job_id,
        "new_settings": new_settings
    }
    
    return make_api_request("POST", "/api/2.0/jobs/update", data=update_data)


async def delete_job(job_id: int) -> Dict[str, Any]:
    """
    Delete a job.
    
    Args:
        job_id: ID of the job to delete
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting job: {job_id}")
    return make_api_request("POST", "/api/2.0/jobs/delete", data={"job_id": job_id})


async def get_run(run_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job run.
    
    Args:
        run_id: ID of the run
        
    Returns:
        Response containing run information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for run: {run_id}")
    return make_api_request("GET", "/api/2.0/jobs/runs/get", params={"run_id": run_id})


async def cancel_run(run_id: int) -> Dict[str, Any]:
    """
    Cancel a job run.

    Args:
        run_id: ID of the run to cancel

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Cancelling run: {run_id}")
    return make_api_request("POST", "/api/2.0/jobs/runs/cancel", data={"run_id": run_id})


async def list_runs(
    job_id: Optional[int] = None,
    active_only: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    List job runs.

    Args:
        job_id: Optional job ID to filter runs. If omitted, returns runs for all jobs.
        active_only: If True, only return active runs (PENDING, RUNNING, TERMINATING).
        limit: Maximum number of runs to return (default 20, max 1000).
        offset: Offset of the first run to return.

    Returns:
        Response containing a list of runs and a has_more flag.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Listing runs for job_id={job_id}, active_only={active_only}")
    params: Dict[str, Any] = {"limit": limit, "offset": offset}
    if job_id is not None:
        params["job_id"] = job_id
    if active_only is not None:
        params["active_only"] = active_only
    return make_api_request("GET", "/api/2.0/jobs/runs/list", params=params)


async def get_run_output(run_id: int) -> Dict[str, Any]:
    """
    Get the output and metadata of a job run task.

    Args:
        run_id: ID of the run

    Returns:
        Response containing run output (up to 5MB) and metadata.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting output for run: {run_id}")
    return make_api_request("GET", "/api/2.0/jobs/runs/get-output", params={"run_id": run_id})


async def cancel_all_runs(job_id: int) -> Dict[str, Any]:
    """
    Cancel all active runs of a job.

    Args:
        job_id: ID of the job whose runs should be cancelled

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Cancelling all runs for job: {job_id}")
    return make_api_request("POST", "/api/2.0/jobs/runs/cancel-all", data={"job_id": job_id})


async def delete_run(run_id: int) -> Dict[str, Any]:
    """
    Delete a non-active job run.

    Args:
        run_id: ID of the run to delete

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting run: {run_id}")
    return make_api_request("POST", "/api/2.0/jobs/runs/delete", data={"run_id": run_id})


async def submit_run(run_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit a one-time run without creating a persistent job.

    Args:
        run_config: Run configuration (same structure as job task settings,
                    e.g. existing_cluster_id or new_cluster, notebook_task, etc.)

    Returns:
        Response containing the run_id of the submitted run.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Submitting one-time run")
    return make_api_request("POST", "/api/2.0/jobs/runs/submit", data=run_config)


async def reset_job(job_id: int, new_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Overwrite all settings of a job with the provided settings.

    Unlike update_job (partial patch), this replaces the entire job configuration.

    Args:
        job_id: ID of the job to reset
        new_settings: Complete new job settings (name, tasks, schedule, etc.)

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Resetting job: {job_id}")
    return make_api_request(
        "POST", "/api/2.0/jobs/reset", data={"job_id": job_id, "new_settings": new_settings}
    )


async def repair_run(
    run_id: int,
    rerun_tasks: Optional[List[str]] = None,
    latest_repair_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Re-run one or more failed or cancelled tasks of an existing run.

    Args:
        run_id: ID of the run to repair
        rerun_tasks: Optional list of task keys to rerun. If omitted, all
                     failed and cancelled tasks are rerun.
        latest_repair_id: ID of the latest repair of the run. Required when
                          issuing multiple consecutive repair requests.

    Returns:
        Response containing the repair_id of the new repair run.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Repairing run: {run_id}")
    data: Dict[str, Any] = {"run_id": run_id}
    if rerun_tasks is not None:
        data["rerun_tasks"] = rerun_tasks
    if latest_repair_id is not None:
        data["latest_repair_id"] = latest_repair_id
    return make_api_request("POST", "/api/2.0/jobs/runs/repair", data=data)
