from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import json


class TimestreamQueryModel:
    def __init__(self, flex_angle_list, fused_angle_list, perp_angle_list, time_start, time_end):
        self.flex_angle_list = flex_angle_list
        self.fused_angle_list = fused_angle_list
        self.perp_angle_list = perp_angle_list
        self.time_start = time_start
        self.time_end = time_end

    def to_json(self):
        return {"flex_angle_list": self.flex_angle_list,
                "fused_angle_list": self.fused_angle_list,
                "perp_angle_list": self.perp_angle_list,
                "time_start": self.time_start,
                "time_end": self.time_end}, 200
