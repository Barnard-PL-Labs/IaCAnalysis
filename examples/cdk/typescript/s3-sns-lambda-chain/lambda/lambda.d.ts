export interface LambdaResponse {
    statusCode: number;
    body: any;
}
export declare const handler: (event: Record<string, any>) => Promise<LambdaResponse>;
