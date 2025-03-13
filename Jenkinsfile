pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
    steps {
        sh '''
            # Only create virtual environment if it doesn't exist
            if [ ! -d "venv" ]; then
                python3 -m venv venv --copies
                chmod -R 755 venv/bin/
            fi
            
            # Use pip cache and only install if requirements have changed
            if [ ! -f ".pip_cache_hash" ] || [ "$(md5sum requirements.txt | awk '{print $1}')" != "$(cat .pip_cache_hash)" ]; then
                echo "Installing dependencies..."
                venv/bin/pip install --upgrade pip --quiet
                venv/bin/pip install -r requirements.txt --quiet
                venv/bin/pip install pytest elasticsearch --quiet
                
                # Save hash of requirements.txt for future comparison
                md5sum requirements.txt | awk '{print $1}' > .pip_cache_hash
            else
                echo "Dependencies up to date, skipping installation"
            fi
            
            # Quick verification of critical packages
            venv/bin/pip list | grep -E 'pytest|elasticsearch' || true
        '''
        
        // Conditional execution of sonar installation
        script {
            def sonarExists = sh(script: 'which sonar-scanner || echo "not found"', returnStdout: true).trim()
            if (sonarExists == "not found") {
                sh 'make install-sonar'
            } else {
                echo "Sonar already installed, skipping"
            }
        }
    }
}
        stage('Start MLflow Server') {
            steps {
                sh 'venv/bin/mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000 &'
                sh 'sleep 10' // Wait for the server to start
            }
        }

        stage('Start Elasticsearch and Kibana') {
    steps {
        sh '''
            # Start Elasticsearch and Kibana
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
        script {
            // Increase Docker build timeout
            timeout(time: 30, unit: 'MINUTES') {
                // Clean up existing images to free space
                sh 'docker system prune -f || true'
                
                // Try direct Docker build command with memory limits
                sh '''
                    echo "Building Docker image..."
                    docker build --memory=2g --memory-swap=2g -t ines253/ines_bennour_mlops .
                '''
            }
        }
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
