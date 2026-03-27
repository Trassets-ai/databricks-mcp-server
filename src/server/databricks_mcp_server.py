"""
Databricks MCP Server

This module implements a standalone MCP server that provides tools for interacting
with Databricks APIs. It follows the Model Context Protocol standard, communicating
via stdio and directly connecting to Databricks when tools are invoked.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

from mcp.server import FastMCP

from src.api import clusters, dbfs, jobs, notebooks, sql
from src.core.config import settings

logger = logging.getLogger(__name__)


async def _run_tool(coro, action: str) -> List[Dict[str, Any]]:
    try:
        result = await coro
        return [{"text": json.dumps(result)}]
    except Exception as e:
        logger.error(f"Error {action}: {str(e)}")
        return [{"text": json.dumps({"error": str(e)})}]


class DatabricksMCPServer(FastMCP):
    """An MCP server for Databricks APIs."""

    def __init__(self):
        """Initialize the Databricks MCP server."""
        super().__init__(name="databricks-mcp",
                         instructions="Use this server to manage Databricks resources")
        logger.info("Initializing Databricks MCP server")
        logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Databricks MCP tools."""

        @self.tool(name="list_clusters", description="List all Databricks clusters")
        async def list_clusters(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Listing clusters with params: {params}")
            return await _run_tool(clusters.list_clusters(), "listing clusters")

        @self.tool(
            name="create_cluster",
            description="Create a new Databricks cluster with parameters: cluster_name (required), spark_version (required), node_type_id (required), num_workers, autotermination_minutes",
        )
        async def create_cluster(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Creating cluster with params: {params}")
            return await _run_tool(clusters.create_cluster(params), "creating cluster")

        @self.tool(
            name="terminate_cluster",
            description="Terminate a Databricks cluster with parameter: cluster_id (required)",
        )
        async def terminate_cluster(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Terminating cluster with params: {params}")
            return await _run_tool(clusters.terminate_cluster(params.get("cluster_id")), "terminating cluster")

        @self.tool(
            name="get_cluster",
            description="Get information about a specific Databricks cluster with parameter: cluster_id (required)",
        )
        async def get_cluster(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Getting cluster info with params: {params}")
            return await _run_tool(clusters.get_cluster(params.get("cluster_id")), "getting cluster info")

        @self.tool(
            name="start_cluster",
            description="Start a terminated Databricks cluster with parameter: cluster_id (required)",
        )
        async def start_cluster(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Starting cluster with params: {params}")
            return await _run_tool(clusters.start_cluster(params.get("cluster_id")), "starting cluster")

        @self.tool(name="list_jobs", description="List all Databricks jobs")
        async def list_jobs(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Listing jobs with params: {params}")
            return await _run_tool(jobs.list_jobs(), "listing jobs")

        @self.tool(
            name="create_job",
            description="Create a new Databricks job. Parameters: job_config (required dict, must include 'name' and task definition such as notebook_task, python_task, etc.)",
        )
        async def create_job(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Creating job with params: {params}")
            return await _run_tool(jobs.create_job(params.get("job_config", params)), "creating job")

        @self.tool(
            name="get_job",
            description="Get details of a Databricks job with parameter: job_id (required)",
        )
        async def get_job(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Getting job with params: {params}")
            return await _run_tool(jobs.get_job(params.get("job_id")), "getting job")

        @self.tool(
            name="update_job",
            description="Partially update a Databricks job with parameters: job_id (required), new_settings (required dict with fields to update)",
        )
        async def update_job(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Updating job with params: {params}")
            return await _run_tool(
                jobs.update_job(params.get("job_id"), params.get("new_settings", {})),
                "updating job",
            )

        @self.tool(
            name="delete_job",
            description="Delete a Databricks job with parameter: job_id (required)",
        )
        async def delete_job(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Deleting job with params: {params}")
            return await _run_tool(jobs.delete_job(params.get("job_id")), "deleting job")

        @self.tool(
            name="run_job",
            description="Trigger a Databricks job run with parameters: job_id (required), notebook_params (optional dict), python_params (optional list of strings), jar_params (optional list of strings), spark_submit_params (optional list of strings)",
        )
        async def run_job(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Running job with params: {params}")
            return await _run_tool(
                jobs.run_job(
                    params.get("job_id"),
                    notebook_params=params.get("notebook_params"),
                    python_params=params.get("python_params"),
                    jar_params=params.get("jar_params"),
                    spark_submit_params=params.get("spark_submit_params"),
                ),
                "running job",
            )

        @self.tool(
            name="list_runs",
            description="List Databricks job runs with parameters: job_id (optional, filter by job), active_only (optional bool, only active runs), limit (optional int, default 20), offset (optional int, default 0)",
        )
        async def list_runs(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Listing runs with params: {params}")
            return await _run_tool(
                jobs.list_runs(
                    job_id=params.get("job_id"),
                    active_only=params.get("active_only"),
                    limit=params.get("limit", 20),
                    offset=params.get("offset", 0),
                ),
                "listing runs",
            )

        @self.tool(
            name="get_run",
            description="Get metadata and status of a Databricks job run with parameter: run_id (required)",
        )
        async def get_run(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Getting run with params: {params}")
            return await _run_tool(jobs.get_run(params.get("run_id")), "getting run")

        @self.tool(
            name="get_run_output",
            description="Get the output of a completed Databricks job run (up to 5MB) with parameter: run_id (required)",
        )
        async def get_run_output(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Getting run output with params: {params}")
            return await _run_tool(jobs.get_run_output(params.get("run_id")), "getting run output")

        @self.tool(
            name="cancel_run",
            description="Cancel an active Databricks job run with parameter: run_id (required)",
        )
        async def cancel_run(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Cancelling run with params: {params}")
            return await _run_tool(jobs.cancel_run(params.get("run_id")), "cancelling run")

        @self.tool(
            name="cancel_all_runs",
            description="Cancel all active runs of a Databricks job with parameter: job_id (required)",
        )
        async def cancel_all_runs(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Cancelling all runs with params: {params}")
            return await _run_tool(jobs.cancel_all_runs(params.get("job_id")), "cancelling all runs")

        @self.tool(
            name="delete_run",
            description="Delete a completed (non-active) Databricks job run with parameter: run_id (required)",
        )
        async def delete_run(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Deleting run with params: {params}")
            return await _run_tool(jobs.delete_run(params.get("run_id")), "deleting run")

        @self.tool(
            name="submit_run",
            description="Submit a one-time Databricks run without creating a persistent job with parameter: run_config (required dict with cluster and task definition)",
        )
        async def submit_run(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Submitting run with params: {params}")
            return await _run_tool(jobs.submit_run(params.get("run_config", params)), "submitting run")

        @self.tool(
            name="list_notebooks",
            description="List notebooks in a workspace directory with parameter: path (required)",
        )
        async def list_notebooks(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Listing notebooks with params: {params}")
            return await _run_tool(notebooks.list_notebooks(params.get("path")), "listing notebooks")

        @self.tool(
            name="export_notebook",
            description="Export a notebook from the workspace with parameters: path (required), format (optional, one of: SOURCE, HTML, JUPYTER, DBC)",
        )
        async def export_notebook(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Exporting notebook with params: {params}")
            try:
                format_type = params.get("format", "SOURCE")
                result = await notebooks.export_notebook(params.get("path"), format_type)
                content = result.get("content", "")
                if len(content) > 1000:
                    result["content"] = f"{content[:1000]}... [content truncated, total length: {len(content)} characters]"
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error exporting notebook: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="list_files",
            description="List files and directories in a DBFS path with parameter: dbfs_path (required)",
        )
        async def list_files(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Listing files with params: {params}")
            return await _run_tool(dbfs.list_files(params.get("dbfs_path")), "listing files")

        @self.tool(
            name="execute_sql",
            description="Execute a SQL statement with parameters: statement (required), warehouse_id (required), catalog (optional), schema (optional)",
        )
        async def execute_sql(params: Dict[str, Any]) -> List[Dict[str, Any]]:
            logger.info(f"Executing SQL with params: {params}")
            return await _run_tool(
                sql.execute_statement(
                    params.get("statement"),
                    params.get("warehouse_id"),
                    params.get("catalog"),
                    params.get("schema"),
                ),
                "executing SQL",
            )


async def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Databricks MCP server")
        server = DatabricksMCPServer()
        
        await server.run_stdio_async()
            
    except Exception as e:
        logger.error(f"Error in Databricks MCP server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Turn off buffering in stdout
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)
    
    asyncio.run(main()) 