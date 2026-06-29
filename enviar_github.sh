#!/bin/bash
git remote remove origin
git remote add origin https://github.com
git branch -M main
git push -u origin main --force
