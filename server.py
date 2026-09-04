#!/usr/bin/env python3
"""启动 demo：python3 server.py   （或 python3 -m aiengine.cli serve）"""
from aiengine.pipeline import PipelineEngine
from aiengine.webserver import serve

if __name__ == "__main__":
    serve(PipelineEngine())
