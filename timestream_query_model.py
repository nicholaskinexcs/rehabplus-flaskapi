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


class TimestreamQueryAccDataModel:
    def __init__(self, x_acc_list, y_acc_list, z_acc_list, temperature_list, position_list, pitch_list, time_start):
        self.x_acc_list = x_acc_list
        self.y_acc_list = y_acc_list
        self.z_acc_list = z_acc_list
        self.temperature_list = temperature_list
        self.position_list = position_list
        self.pitch_list = pitch_list
        self.time_start = time_start

    def to_json(self):
        return {"x_acc_list": self.x_acc_list,
                "y_acc_list": self.y_acc_list,
                "z_acc_list": self.z_acc_list,
                "temperature_list": self.temperature_list,
                "position_list": self.position_list,
                "pitch_list": self.pitch_list,
                "time_start": self.time_start}, 200
