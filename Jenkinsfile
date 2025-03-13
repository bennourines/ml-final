pipeline {
    agent any
    
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    # Remove any existing virtual environment
                    rm -rf venv || true

                    # Create a proper virtual environment with the --copies flag
                    python3 -m venv venv --copies

                    # Set permissions
                    chmod -R 755 venv/bin/

                    # Verify the Python path
                    readlink -f venv/bin/python

                    # Install dependencies
                    venv/bin/pip install --upgrade pip
                    venv/bin/pip install -r requirements.txt
                    venv/bin/pip install pytest --force-reinstall

                    # Install elasticsearch package explicitly
                    venv/bin/pip install elasticsearch

                    # Verify installations
                    venv/bin/pip list | grep pytest
                    venv/bin/pip list | grep elasticsearch
                '''
                sh 'make install-sonar'
            }
        }

        stage('Start MLflow Server') {
            steps {
                sh '''
                    # Start the MLflow server with SQLite backend and default artifact root
                    venv/bin/mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000 &
                    
                    # Sleep to ensure MLflow server is ready
                    sleep 10
                '''
            }
        }

        stage('Start Elasticsearch and Kibana') {
            steps {
                sh '''
                    # Start Elasticsearch and Kibana using Docker
                    docker start elasticsearch kibana || true

                    # Wait for Elasticsearch to be ready
                    echo "Waiting for Elasticsearch to start..."
                    for i in {1..30}; do
                        if curl -s http://localhost:9200 > /dev/null; then
                            echo "Elasticsearch is up!"
                            break
                        fi
                        echo "Waiting for Elasticsearch... ($i/30)"
                        sleep 5
                    done
                '''
            }
        }

        stage('Debug Dependencies') {
            steps {
                sh '''
                    # Debugging installed dependencies
                    venv/bin/pip list | grep urllib3
                    venv/bin/pip show urllib3
                '''
            }
        }

        stage('Debug Environment') {
            steps {
                sh '''
                    # Debugging environment setup
                    pwd
                    which python3
                    python3 --version
                    ls -la venv/bin/
                    venv/bin/pip freeze
                    venv/bin/python -c "import sys; print(sys.path)"
                    find venv -name pytest -type d
                '''
            }
        }

        stage('Run Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        # Run unit and functional tests using pytest
                        venv/bin/python -m pytest tests/unit -v
                        venv/bin/python -m pytest tests/functional -v
                    '''
                }
            }
        }

        stage('CODE QUALITY & SECURITY') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        # Run static code analysis tools
                        venv/bin/python -m pylint **/*.py
                        venv/bin/python -m flake8 .
                        venv/bin/python -m mypy .
                        venv/bin/python -m bandit -r .

                        # Format code using Black
                        venv/bin/python -m black ..
                    '''
                }
            }
        }

        stage('Data Pipeline') {
            steps {
                sh 'make data'
            }
        }

        stage('Training Pipeline') {
            steps {
                sh 'make train'
            }
        }

        stage('Evaluation Pipeline') {
            steps {
                sh 'make evaluate'
            }
        }

        stage('Prompt Check') {
            steps {
                mail to: 'bennourines00@gmail.com',
                     cc: 'bennourines00@gmail.com',
                     subject: "INPUT: Build ${env.JOB_NAME}",
                     body: "Awaiting your input for ${env.JOB_NAME} build no: ${env.BUILD_NUMBER}. Click below to promote to production\n${env.JENKINS_URL}job/${env.JOB_NAME}\n\nView the log at:\n ${env.BUILD_URL}\n\nBlue Ocean:\n${env.RUN_DISPLAY_URL}"
                
                timeout(time: 60, unit: 'MINUTES') {
                    input message: "Promote to Production?", ok: "Promote"
                }
            }
        }
    }

    post {
        always {
            // Clean up to save disk space
            sh 'docker system prune -f || true'
            sh 'find . -name "__pycache__" -type d -exec rm -rf {} +  || true'
            sh 'find . -name "*.pyc" -delete || true'
        }

        failure {
            mail to: 'bennourines00@gmail.com',
                 cc: 'bennourines00@gmail.com',
                 subject: "FAILED: Build ${env.JOB_NAME}",
                 body: "Build failed ${env.JOB_NAME} build no: ${env.BUILD_NUMBER}.\n\nView the log at:\n ${env.BUILD_URL}\n\nBlue Ocean:\n${env.RUN_DISPLAY_URL}"
        }

        success {
            mail to: 'bennourines00@gmail.com',
                 cc: 'bennourines00@gmail.com',
                 subject: "SUCCESSFUL: Build ${env.JOB_NAME}",
                 body: "Build Successful ${env.JOB_NAME} build no: ${env.BUILD_NUMBER}\n\nView the log at:\n ${env.BUILD_URL}\n\nBlue Ocean:\n${env.RUN_DISPLAY_URL}"
        }

        aborted {
            mail to: 'bennourines00@gmail.com',
                 cc: 'bennourines00@gmail.com',
                 subject: "ABORTED: Build ${env.JOB_NAME}",
                 body: "Build was aborted ${env.JOB_NAME} build no: ${env.BUILD_NUMBER}\n\nView the log at:\n ${env.BUILD_URL}\n\nBlue Ocean:\n${env.RUN_DISPLAY_URL}"
        }
    }
}
