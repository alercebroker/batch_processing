#!/bin/bash
#SBATCH -J magstats
#SBATCH -p slims
#SBATCH -n 1
#SBATCH --output=/home/apps/astro/alercebroker/logs/magstats_%A_%a.txt
#SBATCH --error=/home/apps/astro/alercebroker/logs/magstats_%A_%a.err
#SBATCH --mail-user=javier.arredondo.c@usach.cl
#SBATCH --mail-type=ALL
#SBATCH --mem-per-cpu=5000

ml Python/3.7.2
source ~/venvs/env/bin/activate

input_corrected=$1
input_nondet=$2
format=$3
resources='/home/apps/astro/alercebroker/resources/'
output='/home/apps/astro/alercebroker/historic_data/'

export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

python3 ../get_magstats.py $input_corrected $input_nondet $output ${SLURM_ARRAY_TASK_ID} ${SLURM_JOB_NODELIST} ${SLURM_ARRAY_JOB_ID} $resources --file-format $format
