const axios = require('axios');
const config = require('../config/config');
const http = require('http');
const https = require('https');
const fetch = require('node-fetch');

class AIService {
    constructor() {
        this.baseUrl = config.ai.baseUrl;
            
        this.maxRetries = 3;
        this.timeout = config.ai.timeout;
        
        // Create axios instance with custom configuration
        this.axiosInstance = axios.create({
            httpAgent: new http.Agent({ family: 4 }), // Force IPv4
            httpsAgent: new https.Agent({ family: 4 }), // Force IPv4
            timeout: this.timeout,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
    }

    // Regular chat method for non-streaming responses
    async chat(message, llm_name = 'GPT-3.5 Turbo', endpoint = '/agent/chat', agent_id = null) {
        let retries = 0;
        
        while (retries < this.maxRetries) {
            try {
                console.log(`Attempting to call AI service (attempt ${retries + 1}/${this.maxRetries})`);
                const url = `${this.baseUrl}${endpoint}`;
                console.log('Request URL:', url);
                
                // Prepare request data
                const requestData = { 
                    user: message,
                    llm_name
                };
                
                // Add agent_id only if provided
                if (agent_id) {
                    requestData.agent_id = agent_id;
                }
                
                console.log('Request Body:', requestData);
                
                const response = await this.axiosInstance({
                    method: 'post',
                    url: url,
                    data: requestData
                });

                console.log('AI service response:', response.data);
                return response.data;
            } catch (error) {
                retries++;
                console.error(`AI service error (attempt ${retries}/${this.maxRetries}):`, error.message);
                if (error.response) {
                    console.error('Error Response Data:', error.response.data);
                    console.error('Error Response Status:', error.response.status);
                    console.error('Error Response Headers:', error.response.headers);
                } else if (error.request) {
                    console.error('No response received from AI service');
                } else {
                    console.error('Error setting up the request:', error.message);
                }
                
                if (retries === this.maxRetries) {
                    throw new Error('AI service is currently unavailable. Please try again later.');
                }
                
                const backoffTime = 1000 * Math.pow(2, retries);
                console.log(`Waiting ${backoffTime}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, backoffTime));
            }
        }
    }

    // Streaming chat method
    async chatStream(message, llmName, endpoint = '/agent/chat/stream') {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            console.log('Starting streaming chat request');
            console.log('Request URL:', url);
            console.log('Request Body:', { user: message, llm_name: llmName });

            // Log the full request details
            console.log('Full request details:', {
                url,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                },
                body: { user: message, llm_name: llmName }
            });

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                },
                body: JSON.stringify({
                    user: message,
                    llm_name: llmName
                })
            });

            console.log('Stream response status:', response.status);
            console.log('Stream response headers:', Object.fromEntries(response.headers.entries()));

            if (!response.ok) {
                const error = await response.text();
                console.error('Streaming request failed:', {
                    status: response.status,
                    statusText: response.statusText,
                    error
                });
                throw new Error(`HTTP error! status: ${response.status} - ${error}`);
            }

            if (!response.body) {
                console.error('No response body received');
                throw new Error('No response body received from AI service');
            }

            console.log('Successfully established stream connection');
            return response.body;
        } catch (error) {
            console.error('Error in chat stream:', error);
            // Log the full error details
            if (error.response) {
                console.error('Error response:', {
                    status: error.response.status,
                    headers: error.response.headers,
                    data: error.response.data
                });
            }
            throw error;
        }
    }
}

module.exports = new AIService(); 