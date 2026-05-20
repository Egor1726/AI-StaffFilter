#!/bin/bash
export PATH=$HOME/work/AI-StaffFilter/.env/bin:$PATH
cd ~/work/AI-StaffFilter/frontend
npm install
npm run dev -- --host 0.0.0.0