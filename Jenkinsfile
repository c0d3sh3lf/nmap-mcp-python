pipeline {
  environment {
    dockerimagename = "invad3rsam/nmap-mcp-python"
    dockerImage = ""
    recepientEmail = "sumit.shrivastava65@gmail.com"
    img_tag = ""
  }
  agent any
  stages {
    // stage('Checkout Source') {
    //   steps {
    //     checkout scm: [$class: 'GitSCM',
    //     branches: [[name: '*/development']],
    //     userRemoteConfigs: [[credentialsId: 'github-fa-token', 
    //     url: 'https://github.com/c0d3sh3lf/react-ci-k8s-test']]]
    //   }
    // }
    stage('Build image') {
      steps{
        script {
          dockerImage = docker.build dockerimagename
        }
      }
    }
    stage('Pushing Image') {
      environment {
               registryCredential = 'docker-hub'
           }
      steps{
        script {
          def now = new Date()
          img_tag = now.format("yyMMdd.HHmm", TimeZone.getTimeZone('UTC'))
          docker.withRegistry( 'https://registry.hub.docker.com', registryCredential ) {
            dockerImage.push("${img_tag}")
            // dockerImage.push("latest")
          }
        }
      }
    }
    stage('Deploying React.js container to Kubernetes') {
      steps {
        script {
          sh 'kubectl apply -f service.yaml'
          sh 'kubectl apply -f deployment.yaml'
          sh 'kubectl apply -f service.yaml'
        }
      }
    }
  }
  post {
    always {
      emailext to: "sumit.shrivastava65@gmail.com",
      from: 'Jenkins (noreply.jenkins.sam@gmail.com)',
      subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME}",
      body: "${currentBuild.currentResult}: Job ${env.JOB_NAME}\nMore Info can be found here: ${env.BUILD_URL}",
      mimeType: 'text/html',
      attachLog: true // Attach the build log to the email
    }
    success {
      script {
        sh "curl -H \"Title: ${currentBuild.currentResult} - ${env.JOB_NAME} #${currentBuild.number}\" -H \"Tags: green_circle\" -d \"${currentBuild.currentResult} for jenkins job ${env.JOB_NAME} for build number ${currentBuild.number}. More info at ${env.BUILD_URL}.\" -k https://ntfy.invadersam.cloud/sam_alerts"
      }
    }

    failure {
      script {
        sh "curl -H \"Title: ${currentBuild.currentResult} - ${env.JOB_NAME} #${currentBuild.number}\" -H \"Tags: red_circle\" -d \"${currentBuild.currentResult} for jenkins job ${env.JOB_NAME} for build number ${currentBuild.number}. More info at ${env.BUILD_URL}.\" -k https://ntfy.invadersam.cloud/sam_alerts"
      }
    }
  }
}