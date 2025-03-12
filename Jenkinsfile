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
            
            # Verify pytest installation
            venv/bin/pip list | grep pytest
        '''
        sh 'make install-sonar'
    }
}

        stage('Start MLflow Server') {
            steps {
                sh 'venv/bin/mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000 &'
                sh 'sleep 10' // Wait for the server to start
            }
        }

        stage('Debug Dependencies') {
            steps {
                sh 'venv/bin/pip list | grep urllib3'
                sh 'venv/bin/pip show urllib3'
            }
        }
        
        stage('Debug Environment') {
    steps {
        sh 'pwd'
        sh 'which python3'
        sh 'python3 --version'
        sh 'ls -la venv/bin/'
        sh 'venv/bin/pip freeze'
        sh 'venv/bin/python -c "import sys; print(sys.path)"'
        sh 'find venv -name pytest -type d'
    }
}

        stage('Run Tests') {
    steps {
        sh '''
            # Directly run tests with the Python interpreter
            venv/bin/python -m pytest tests/unit -v
            venv/bin/python -m pytest tests/functional -v
        '''
    }
}
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    sh 'export PATH=$PATH:/opt/sonar-scanner/bin && make sonar'
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

        stage('Build Docker Image') {
            steps {
                sh 'make docker-build'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_HUB_USER', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
                    sh 'docker login -u $DOCKER_HUB_USER -p $DOCKER_HUB_PASSWORD'
                    sh 'make docker-push'
                }
            }
        }

        stage('Deploy') {
            steps {
                sh 'make docker-run'
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
        success {
            emailext (
                body: """
                <html>
                <body>
                <h2>✅ Pipeline Successful</h2>
                <p>Build: ${env.BUILD_NUMBER}</p>
                <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>
                </body>
                </html>
                """,
                subject: "✅ Pipeline Success: ${env.JOB_NAME} [${env.BUILD_NUMBER}]",
                to: 'bennourines00@gmail.com',
                mimeType: 'text/html'
            )
        }
        failure {
            emailext (
                body: """
                <html>
                <body>
                <h2>❌ Pipeline Failed</h2>
                <p>Build: ${env.BUILD_NUMBER}</p>
                <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>
                </body>
                </html>
                """,
                subject: "❌ Pipeline Failed: ${env.JOB_NAME} [${env.BUILD_NUMBER}]",
                to: 'bennourines00@gmail.com',
                mimeType: 'text/html'
            )
        }
    }
}
