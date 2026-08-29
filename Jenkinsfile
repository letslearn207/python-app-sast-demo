pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        PYTHON_VERSION = '3.11'
        VENV_DIR = "${WORKSPACE}/venv"
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        ARTIFACTORY_URL = credentials('artifactory-url')
        DOCKER_REGISTRY = credentials('docker-registry')
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code from repository..."
                }
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                script {
                    echo "🔧 Setting up Python environment..."
                }
                sh '''
                    python${PYTHON_VERSION} -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt 2>/dev/null || pip install flask
                    pip install pylint flake8 pytest pytest-cov bandit safety
                '''
            }
        }

        stage('Code Quality - Linting') {
            steps {
                script {
                    echo "🔍 Running code quality checks..."
                }
                sh '''
                    . ${VENV_DIR}/bin/activate
                    
                    echo "Running pylint..."
                    pylint app.py --exit-zero --output-format=parseable | tee pylint-report.txt || true
                    
                    echo "Running flake8..."
                    flake8 app.py --format=json > flake8-report.json || true
                '''
            }
        }

        stage('Security Scanning - SAST') {
            parallel {
                stage('Bandit') {
                    steps {
                        script {
                            echo "🛡️ Running Bandit security scan..."
                        }
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            bandit -r . -f json -o bandit-report.json || true
                            bandit -r . -f txt || true
                        '''
                    }
                }

                stage('Safety Check') {
                    steps {
                        script {
                            echo "📦 Checking dependencies for vulnerabilities..."
                        }
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            safety check --json > safety-report.json || true
                        '''
                    }
                }

                stage('SonarQube Scan') {
                    steps {
                        script {
                            echo "☁️ Running SonarQube analysis..."
                        }
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            pip install sonar-python
                            sonar-scanner \
                              -Dsonar.projectKey=python-app-sast-demo \
                              -Dsonar.sources=. \
                              -Dsonar.host.url=${SONARQUBE_HOST} \
                              -Dsonar.login=${SONARQUBE_TOKEN} || true
                        '''
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    echo "✅ Running unit tests..."
                }
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml || true
                '''
            }
        }

        stage('Build Artifacts') {
            steps {
                script {
                    echo "📦 Building application artifacts..."
                }
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install build twine
                    python -m build || true
                '''
            }
        }

        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🐳 Building Docker image..."
                }
                sh '''
                    docker build -t ${DOCKER_REGISTRY}/python-app-sast-demo:${BUILD_NUMBER} .
                    docker tag ${DOCKER_REGISTRY}/python-app-sast-demo:${BUILD_NUMBER} ${DOCKER_REGISTRY}/python-app-sast-demo:latest
                '''
            }
        }

        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "📤 Pushing image to registry..."
                }
                sh '''
                    docker push ${DOCKER_REGISTRY}/python-app-sast-demo:${BUILD_NUMBER}
                    docker push ${DOCKER_REGISTRY}/python-app-sast-demo:latest
                '''
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🚀 Deploying to staging environment..."
                }
                sh '''
                    echo "Deploy command would run here"
                    # Add your deployment logic here
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "📊 Collecting test and scan reports..."
            }
            
            // Archive reports
            archiveArtifacts artifacts: '*-report.*,test-results.xml,*.html', 
                            allowEmptyArchive: true
            
            // Publish test results
            junit testResults: 'test-results.xml', 
                  allowEmptyResults: true
            
            // Publish code coverage
            publishHTML([
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Code Coverage Report'
            ])
        }
        
        success {
            script {
                echo "✅ Pipeline completed successfully!"
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed! Check the logs above for details."
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline is unstable. Review the reports."
            }
        }
    }
}
