#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, jsonify
import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')
        self.reports = {}

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash,
            'reports': []
        }
        self.chain.append(block)
        return block

    def add_report(self, value, diagnosis, key):
        report = {
            'stress_value': value,
            'diagnosis': diagnosis
        }
        if key in self.reports:
            self.reports[key].append(report)
        else:
            self.reports[key] = [report]
        self.get_last_block()['reports'].extend(self.reports[key])
        return True

    def get_last_block(self):
        return self.chain[-1]

    def retrieve_reports(self, key):
        reports = self.reports.get(key, None)
        if reports is None:
            return "No reports found for this key."
        else:
            return reports

blockchain = Blockchain()

app = Flask(__name__)

@app.route('/add_report', methods=['POST'])
def add_report():
    data = request.get_json()
    stress_value = data.get('stress_value')
    key = data.get('key')

    if not isinstance(stress_value, int) or stress_value < 1 or stress_value > 10:
        return jsonify({'message': 'Invalid stress value. Please enter a value between 1 and 10.'}), 400

    if stress_value <= 3:
        diagnosis = "Stress level is in control."
    elif stress_value <= 7:
        diagnosis = "Moderate stress level. Recommend stress management techniques."
    else:
        diagnosis = "Consult a doctor, your stress level is very high."

    success = blockchain.add_report(stress_value, diagnosis, key)
    if success:
        return jsonify({'message': 'Medical report created and saved successfully!'}), 201
    else:
        return jsonify({'message': 'An error occurred while saving the report.'}), 500

@app.route('/retrieve_reports', methods=['GET'])
def retrieve_reports():
    key = request.args.get('key')
    if not key:
        return jsonify({'message': 'Key is required.'}), 400

    reports = blockchain.retrieve_reports(key)
    if isinstance(reports, list):
        return jsonify({'reports': reports}), 200
    else:
        return jsonify({'message': reports}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
