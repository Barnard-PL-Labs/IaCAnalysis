"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventBridgeLambdaStack = void 0;
const events = require("aws-cdk-lib/aws-events");
const targets = require("aws-cdk-lib/aws-events-targets");
const lambda = require("aws-cdk-lib/aws-lambda");
const cdk = require("aws-cdk-lib");
const fs = require("fs");
const sns = require("aws-cdk-lib/aws-sns");
const subscriptions = require("aws-cdk-lib/aws-sns-subscriptions");
const iam = require("aws-cdk-lib/aws-iam");
const aws_cdk_lib_1 = require("aws-cdk-lib");
class EventBridgeLambdaStack extends cdk.Stack {
    constructor(app, id) {
        super(app, id);
        // SNS Topic
        const topic = new sns.Topic(this, 'Topic', {
            displayName: 'Lambda SNS Topic',
        });
        //Email Variable
        const emailaddress = new aws_cdk_lib_1.CfnParameter(this, "email", {
            type: "String",
            description: "The name of the Amazon S3 bucket where uploaded files will be stored."
        });
        // Subscription to the topic
        topic.addSubscription(new subscriptions.EmailSubscription(emailaddress.valueAsString));
        // Lambda Function to publish message to SNS
        const lambdaFn = new lambda.Function(this, 'Singleton', {
            code: new lambda.InlineCode(fs.readFileSync('lambda-handler.py', { encoding: 'utf-8' })),
            handler: 'index.main',
            timeout: cdk.Duration.seconds(300),
            runtime: lambda.Runtime.PYTHON_3_9,
            environment: { 'TOPIC_ARN': topic.topicArn }
        });
        // Run the eventbridge every minute
        const rule = new events.Rule(this, 'Rule', {
            schedule: events.Schedule.expression('cron(* * ? * * *)')
        });
        // Add the lambda function as a target to the eventbridge
        rule.addTarget(new targets.LambdaFunction(lambdaFn));
        // Add the permission to the lambda function to publish to SNS
        const snsTopicPolicy = new iam.PolicyStatement({
            actions: ['sns:publish'],
            resources: ['*'],
        });
        // Add the permission to the lambda function to publish to SNS
        lambdaFn.addToRolePolicy(snsTopicPolicy);
    }
}
exports.EventBridgeLambdaStack = EventBridgeLambdaStack;
const app = new cdk.App();
new EventBridgeLambdaStack(app, 'EventBridgeLambdaStack');
app.synth();
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiaW5kZXguanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJpbmRleC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFBQSxpREFBa0Q7QUFDbEQsMERBQTJEO0FBQzNELGlEQUFrRDtBQUNsRCxtQ0FBb0M7QUFDcEMseUJBQTBCO0FBQzFCLDJDQUE0QztBQUM1QyxtRUFBb0U7QUFDcEUsMkNBQTRDO0FBQzVDLDZDQUEyQztBQUkzQyxNQUFhLHNCQUF1QixTQUFRLEdBQUcsQ0FBQyxLQUFLO0lBQ25ELFlBQVksR0FBWSxFQUFFLEVBQVU7UUFDbEMsS0FBSyxDQUFDLEdBQUcsRUFBRSxFQUFFLENBQUMsQ0FBQztRQUVmLFlBQVk7UUFDWixNQUFNLEtBQUssR0FBRyxJQUFJLEdBQUcsQ0FBQyxLQUFLLENBQUMsSUFBSSxFQUFFLE9BQU8sRUFBRTtZQUN6QyxXQUFXLEVBQUUsa0JBQWtCO1NBQ2hDLENBQUMsQ0FBQztRQUVILGdCQUFnQjtRQUNoQixNQUFNLFlBQVksR0FBRyxJQUFJLDBCQUFZLENBQUMsSUFBSSxFQUFFLE9BQU8sRUFBRTtZQUNuRCxJQUFJLEVBQUUsUUFBUTtZQUNkLFdBQVcsRUFBRSx1RUFBdUU7U0FBQyxDQUFDLENBQUM7UUFFekYsNEJBQTRCO1FBQzVCLEtBQUssQ0FBQyxlQUFlLENBQUMsSUFBSSxhQUFhLENBQUMsaUJBQWlCLENBQUMsWUFBWSxDQUFDLGFBQWEsQ0FBQyxDQUFDLENBQUM7UUFFdkYsNENBQTRDO1FBQzVDLE1BQU0sUUFBUSxHQUFHLElBQUksTUFBTSxDQUFDLFFBQVEsQ0FBQyxJQUFJLEVBQUUsV0FBVyxFQUFFO1lBQ3RELElBQUksRUFBRSxJQUFJLE1BQU0sQ0FBQyxVQUFVLENBQUMsRUFBRSxDQUFDLFlBQVksQ0FBQyxtQkFBbUIsRUFBRSxFQUFFLFFBQVEsRUFBRSxPQUFPLEVBQUUsQ0FBQyxDQUFDO1lBQ3hGLE9BQU8sRUFBRSxZQUFZO1lBQ3JCLE9BQU8sRUFBRSxHQUFHLENBQUMsUUFBUSxDQUFDLE9BQU8sQ0FBQyxHQUFHLENBQUM7WUFDbEMsT0FBTyxFQUFFLE1BQU0sQ0FBQyxPQUFPLENBQUMsVUFBVTtZQUNsQyxXQUFXLEVBQUUsRUFBQyxXQUFXLEVBQUUsS0FBSyxDQUFDLFFBQVEsRUFBQztTQUUzQyxDQUFDLENBQUM7UUFFSCxtQ0FBbUM7UUFDbkMsTUFBTSxJQUFJLEdBQUcsSUFBSSxNQUFNLENBQUMsSUFBSSxDQUFDLElBQUksRUFBRSxNQUFNLEVBQUU7WUFDekMsUUFBUSxFQUFFLE1BQU0sQ0FBQyxRQUFRLENBQUMsVUFBVSxDQUFDLG1CQUFtQixDQUFDO1NBQzFELENBQUMsQ0FBQztRQUVILHlEQUF5RDtRQUN6RCxJQUFJLENBQUMsU0FBUyxDQUFDLElBQUksT0FBTyxDQUFDLGNBQWMsQ0FBQyxRQUFRLENBQUMsQ0FBQyxDQUFDO1FBRXJELDhEQUE4RDtRQUM5RCxNQUFNLGNBQWMsR0FBRyxJQUFJLEdBQUcsQ0FBQyxlQUFlLENBQUM7WUFDN0MsT0FBTyxFQUFFLENBQUMsYUFBYSxDQUFDO1lBQ3hCLFNBQVMsRUFBRSxDQUFDLEdBQUcsQ0FBQztTQUNqQixDQUFDLENBQUM7UUFFSCw4REFBOEQ7UUFDOUQsUUFBUSxDQUFDLGVBQWUsQ0FBQyxjQUFjLENBQUMsQ0FBQztJQUUzQyxDQUFDO0NBQ0Y7QUE3Q0Qsd0RBNkNDO0FBRUQsTUFBTSxHQUFHLEdBQUcsSUFBSSxHQUFHLENBQUMsR0FBRyxFQUFFLENBQUM7QUFDMUIsSUFBSSxzQkFBc0IsQ0FBQyxHQUFHLEVBQUUsd0JBQXdCLENBQUMsQ0FBQztBQUMxRCxHQUFHLENBQUMsS0FBSyxFQUFFLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgZXZlbnRzID0gcmVxdWlyZSgnYXdzLWNkay1saWIvYXdzLWV2ZW50cycpO1xuaW1wb3J0IHRhcmdldHMgPSByZXF1aXJlKCdhd3MtY2RrLWxpYi9hd3MtZXZlbnRzLXRhcmdldHMnKTtcbmltcG9ydCBsYW1iZGEgPSByZXF1aXJlKCdhd3MtY2RrLWxpYi9hd3MtbGFtYmRhJyk7XG5pbXBvcnQgY2RrID0gcmVxdWlyZSgnYXdzLWNkay1saWInKTtcbmltcG9ydCBmcyA9IHJlcXVpcmUoJ2ZzJyk7XG5pbXBvcnQgc25zID0gcmVxdWlyZSgnYXdzLWNkay1saWIvYXdzLXNucycpO1xuaW1wb3J0IHN1YnNjcmlwdGlvbnMgPSByZXF1aXJlKCdhd3MtY2RrLWxpYi9hd3Mtc25zLXN1YnNjcmlwdGlvbnMnKTtcbmltcG9ydCBpYW0gPSByZXF1aXJlKCdhd3MtY2RrLWxpYi9hd3MtaWFtJyk7XG5pbXBvcnQgeyBDZm5QYXJhbWV0ZXIgfSBmcm9tICdhd3MtY2RrLWxpYic7XG5cblxuXG5leHBvcnQgY2xhc3MgRXZlbnRCcmlkZ2VMYW1iZGFTdGFjayBleHRlbmRzIGNkay5TdGFjayB7XG4gIGNvbnN0cnVjdG9yKGFwcDogY2RrLkFwcCwgaWQ6IHN0cmluZykge1xuICAgIHN1cGVyKGFwcCwgaWQpO1xuXG4gICAgLy8gU05TIFRvcGljXG4gICAgY29uc3QgdG9waWMgPSBuZXcgc25zLlRvcGljKHRoaXMsICdUb3BpYycsIHtcbiAgICAgIGRpc3BsYXlOYW1lOiAnTGFtYmRhIFNOUyBUb3BpYycsXG4gICAgfSk7XG5cbiAgICAvL0VtYWlsIFZhcmlhYmxlXG4gICAgY29uc3QgZW1haWxhZGRyZXNzID0gbmV3IENmblBhcmFtZXRlcih0aGlzLCBcImVtYWlsXCIsIHtcbiAgICAgIHR5cGU6IFwiU3RyaW5nXCIsXG4gICAgICBkZXNjcmlwdGlvbjogXCJUaGUgbmFtZSBvZiB0aGUgQW1hem9uIFMzIGJ1Y2tldCB3aGVyZSB1cGxvYWRlZCBmaWxlcyB3aWxsIGJlIHN0b3JlZC5cIn0pO1xuXG4gICAgLy8gU3Vic2NyaXB0aW9uIHRvIHRoZSB0b3BpY1xuICAgIHRvcGljLmFkZFN1YnNjcmlwdGlvbihuZXcgc3Vic2NyaXB0aW9ucy5FbWFpbFN1YnNjcmlwdGlvbihlbWFpbGFkZHJlc3MudmFsdWVBc1N0cmluZykpO1xuXG4gICAgLy8gTGFtYmRhIEZ1bmN0aW9uIHRvIHB1Ymxpc2ggbWVzc2FnZSB0byBTTlNcbiAgICBjb25zdCBsYW1iZGFGbiA9IG5ldyBsYW1iZGEuRnVuY3Rpb24odGhpcywgJ1NpbmdsZXRvbicsIHtcbiAgICAgIGNvZGU6IG5ldyBsYW1iZGEuSW5saW5lQ29kZShmcy5yZWFkRmlsZVN5bmMoJ2xhbWJkYS1oYW5kbGVyLnB5JywgeyBlbmNvZGluZzogJ3V0Zi04JyB9KSksXG4gICAgICBoYW5kbGVyOiAnaW5kZXgubWFpbicsXG4gICAgICB0aW1lb3V0OiBjZGsuRHVyYXRpb24uc2Vjb25kcygzMDApLFxuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuUFlUSE9OXzNfOSxcbiAgICAgIGVudmlyb25tZW50OiB7J1RPUElDX0FSTic6IHRvcGljLnRvcGljQXJufVxuICAgICAgXG4gICAgfSk7XG5cbiAgICAvLyBSdW4gdGhlIGV2ZW50YnJpZGdlIGV2ZXJ5IG1pbnV0ZVxuICAgIGNvbnN0IHJ1bGUgPSBuZXcgZXZlbnRzLlJ1bGUodGhpcywgJ1J1bGUnLCB7XG4gICAgICBzY2hlZHVsZTogZXZlbnRzLlNjaGVkdWxlLmV4cHJlc3Npb24oJ2Nyb24oKiAqID8gKiAqICopJylcbiAgICB9KTtcblxuICAgIC8vIEFkZCB0aGUgbGFtYmRhIGZ1bmN0aW9uIGFzIGEgdGFyZ2V0IHRvIHRoZSBldmVudGJyaWRnZVxuICAgIHJ1bGUuYWRkVGFyZ2V0KG5ldyB0YXJnZXRzLkxhbWJkYUZ1bmN0aW9uKGxhbWJkYUZuKSk7XG5cbiAgICAvLyBBZGQgdGhlIHBlcm1pc3Npb24gdG8gdGhlIGxhbWJkYSBmdW5jdGlvbiB0byBwdWJsaXNoIHRvIFNOU1xuICAgIGNvbnN0IHNuc1RvcGljUG9saWN5ID0gbmV3IGlhbS5Qb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgYWN0aW9uczogWydzbnM6cHVibGlzaCddLFxuICAgICAgcmVzb3VyY2VzOiBbJyonXSxcbiAgICB9KTtcblxuICAgIC8vIEFkZCB0aGUgcGVybWlzc2lvbiB0byB0aGUgbGFtYmRhIGZ1bmN0aW9uIHRvIHB1Ymxpc2ggdG8gU05TXG4gICAgbGFtYmRhRm4uYWRkVG9Sb2xlUG9saWN5KHNuc1RvcGljUG9saWN5KTtcblxuICB9XG59XG5cbmNvbnN0IGFwcCA9IG5ldyBjZGsuQXBwKCk7XG5uZXcgRXZlbnRCcmlkZ2VMYW1iZGFTdGFjayhhcHAsICdFdmVudEJyaWRnZUxhbWJkYVN0YWNrJyk7XG5hcHAuc3ludGgoKTtcbiJdfQ==