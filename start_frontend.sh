#!/bin/bash
export PATH=$HOME/work/AI-StaffFilter/.env/bin:$PATH
cd ~/work/AI-StaffFilter/frontend
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 5173
