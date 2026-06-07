// Flowchart.js - React component for Personal Digital Identity Protection System architecture visualization
import React from 'react';
import { Shield, Database, AlertTriangle, CheckCircle, Users, Lock } from 'lucide-react';

const FlowChart = () => {
  return (
    <div className="w-full h-full bg-gradient-to-br from-blue-50 to-indigo-50 p-8 overflow-auto">
      <div className="max-w-7xl mx-auto">
        
        {/* Title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-indigo-900 mb-2">
            Personal Digital Identity Protection System
          </h1>
          <p className="text-lg text-gray-600">Real-Time Breach Monitoring Architecture</p>
        </div>

        {/* Main Flow */}
        <div className="space-y-8">
          
          {/* Layer 1: Data Sources */}
          <div className="text-center">
            <div className="inline-block bg-indigo-600 text-white px-8 py-3 rounded-lg text-xl font-bold mb-6">
              Data Sources Layer
            </div>
            <div className="flex justify-center gap-6 flex-wrap">
              <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-blue-300 w-64">
                <Database className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                <h3 className="font-bold text-lg mb-2">Breach Databases</h3>
                <p className="text-sm text-gray-600">Have I Been Pwned API</p>
                <p className="text-xs text-gray-500 mt-2">10B+ credentials<br/>500+ breaches</p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-green-300 w-64">
                <Database className="w-12 h-12 text-green-600 mx-auto mb-3" />
                <h3 className="font-bold text-lg mb-2">Paste Sites</h3>
                <p className="text-sm text-gray-600">Pastebin, Ghostbin</p>
                <p className="text-xs text-gray-500 mt-2">Early detection<br/>Pattern recognition</p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-purple-300 w-64">
                <Database className="w-12 h-12 text-purple-600 mx-auto mb-3" />
                <h3 className="font-bold text-lg mb-2">Dark Web</h3>
                <p className="text-sm text-gray-600">Tor Marketplaces</p>
                <p className="text-xs text-gray-500 mt-2">Proactive monitoring<br/>(Future)</p>
              </div>
            </div>
            
            {/* Arrow down */}
            <div className="flex justify-center my-6">
              <div className="w-1 h-12 bg-indigo-400"></div>
            </div>
          </div>

          {/* Layer 2: Data Aggregation & Processing */}
          <div className="text-center">
            <div className="inline-block bg-indigo-600 text-white px-8 py-3 rounded-lg text-xl font-bold mb-6">
              Processing Layer
            </div>
            <div className="flex justify-center gap-6 flex-wrap">
              <div className="bg-purple-100 p-6 rounded-xl shadow-lg border-2 border-purple-400 w-80">
                <h3 className="font-bold text-lg mb-3">Data Aggregation Service</h3>
                <ul className="text-sm text-left space-y-2">
                  <li>✓ Multi-source integration</li>
                  <li>✓ Hash-based deduplication</li>
                  <li>✓ Data normalization</li>
                  <li>✓ Credential matching</li>
                </ul>
              </div>
              
              <div className="bg-orange-100 p-6 rounded-xl shadow-lg border-2 border-orange-400 w-80">
                <h3 className="font-bold text-lg mb-3">Differential Detection</h3>
                <ul className="text-sm text-left space-y-2">
                  <li>✓ Compare with historical data</li>
                  <li>✓ Identify NEW breaches only</li>
                  <li>✓ Timestamp tracking</li>
                  <li>✓ Alert fatigue prevention</li>
                </ul>
              </div>
            </div>
            
            {/* Arrow down */}
            <div className="flex justify-center my-6">
              <div className="w-1 h-12 bg-indigo-400"></div>
            </div>
          </div>

          {/* Layer 3: Risk Assessment */}
          <div className="text-center">
            <div className="inline-block bg-indigo-600 text-white px-8 py-3 rounded-lg text-xl font-bold mb-6">
              Intelligence Layer
            </div>
            <div className="flex justify-center">
              <div className="bg-red-100 p-8 rounded-xl shadow-lg border-2 border-red-400 w-96">
                <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-3" />
                <h3 className="font-bold text-xl mb-4">Risk Assessment Engine</h3>
                <div className="text-left space-y-3">
                  <div className="bg-white p-3 rounded">
                    <span className="font-semibold">Data Sensitivity (40%):</span>
                    <p className="text-sm text-gray-600">Password=10, SSN=10, Email=3</p>
                  </div>
                  <div className="bg-white p-3 rounded">
                    <span className="font-semibold">Breach Recency (30%):</span>
                    <p className="text-sm text-gray-600">0-30 days=10, 365 days=2</p>
                  </div>
                  <div className="bg-white p-3 rounded">
                    <span className="font-semibold">Source Credibility (20%):</span>
                    <p className="text-sm text-gray-600">Confirmed=10, Suspected=3</p>
                  </div>
                  <div className="bg-white p-3 rounded">
                    <span className="font-semibold">Exposure Scope (10%):</span>
                    <p className="text-sm text-gray-600">10M=10, 100K=3</p>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-yellow-200 rounded font-bold">
                  Severity Score: Critical | High | Medium | Low
                </div>
              </div>
            </div>
            
            {/* Arrow down */}
            <div className="flex justify-center my-6">
              <div className="w-1 h-12 bg-indigo-400"></div>
            </div>
          </div>

          {/* Layer 4: Alert Generation */}
          <div className="text-center">
            <div className="inline-block bg-indigo-600 text-white px-8 py-3 rounded-lg text-xl font-bold mb-6">
              Alert Layer
            </div>
            <div className="flex justify-center gap-6 flex-wrap">
              <div className="bg-yellow-100 p-6 rounded-xl shadow-lg border-2 border-yellow-400 w-72">
                <h3 className="font-bold text-lg mb-3">Personalized Recommendations</h3>
                <div className="text-left text-sm space-y-2">
                  <div className="bg-red-200 p-2 rounded">
                    <strong>Critical:</strong> Change password NOW
                  </div>
                  <div className="bg-orange-200 p-2 rounded">
                    <strong>High:</strong> Change within 24hrs
                  </div>
                  <div className="bg-yellow-200 p-2 rounded">
                    <strong>Medium:</strong> Schedule update
                  </div>
                  <div className="bg-blue-200 p-2 rounded">
                    <strong>Low:</strong> Monitor activity
                  </div>
                </div>
              </div>
              
              <div className="bg-green-100 p-6 rounded-xl shadow-lg border-2 border-green-400 w-72">
                <h3 className="font-bold text-lg mb-3">Multi-Channel Delivery</h3>
                <ul className="text-sm text-left space-y-2">
                  <li>📧 Email notifications</li>
                  <li>🔔 In-app dashboard alerts</li>
                  <li>📱 Push notifications (future)</li>
                  <li>⚡ <strong>&lt;5 min delivery time</strong></li>
                </ul>
              </div>
            </div>
            
            {/* Arrow down */}
            <div className="flex justify-center my-6">
              <div className="w-1 h-12 bg-indigo-400"></div>
            </div>
          </div>

          {/* Layer 5: User Interface */}
          <div className="text-center">
            <div className="inline-block bg-indigo-600 text-white px-8 py-3 rounded-lg text-xl font-bold mb-6">
              User Layer
            </div>
            <div className="flex justify-center">
              <div className="bg-blue-100 p-8 rounded-xl shadow-lg border-2 border-blue-400 w-full max-w-2xl">
                <Users className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                <h3 className="font-bold text-xl mb-4">User Dashboard & Action</h3>
                <div className="grid grid-cols-2 gap-4 text-left">
                  <div className="bg-white p-4 rounded">
                    <h4 className="font-semibold mb-2">View Breaches</h4>
                    <p className="text-sm text-gray-600">Timeline, severity, details</p>
                  </div>
                  <div className="bg-white p-4 rounded">
                    <h4 className="font-semibold mb-2">Security Score</h4>
                    <p className="text-sm text-gray-600">Risk visualization</p>
                  </div>
                  <div className="bg-white p-4 rounded">
                    <h4 className="font-semibold mb-2">Action Checklists</h4>
                    <p className="text-sm text-gray-600">Step-by-step guidance</p>
                  </div>
                  <div className="bg-white p-4 rounded">
                    <h4 className="font-semibold mb-2">Monitor Settings</h4>
                    <p className="text-sm text-gray-600">Add/remove identities</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Layer 6: Automation & Security */}
          <div className="mt-12 grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-purple-100 to-purple-200 p-6 rounded-xl shadow-lg border-2 border-purple-400">
              <h3 className="font-bold text-xl mb-4 flex items-center gap-2">
                <CheckCircle className="w-6 h-6 text-purple-600" />
                Automation Layer
              </h3>
              <ul className="space-y-2 text-sm">
                <li>✓ GitHub Actions: Daily scans at 02:00 UTC</li>
                <li>✓ Parallel processing for scalability</li>
                <li>✓ Automated retry with exponential backoff</li>
                <li>✓ Circuit breaker for failed services</li>
                <li>✓ Zero manual intervention required</li>
              </ul>
            </div>
            
            <div className="bg-gradient-to-br from-green-100 to-green-200 p-6 rounded-xl shadow-lg border-2 border-green-400">
              <h3 className="font-bold text-xl mb-4 flex items-center gap-2">
                <Lock className="w-6 h-6 text-green-600" />
                Security Layer
              </h3>
              <ul className="space-y-2 text-sm">
                <li>🔒 JWT authentication + Bcrypt hashing</li>
                <li>🔒 AES-256-GCM encryption at rest</li>
                <li>🔒 TLS 1.3 encryption in transit</li>
                <li>🔒 K-anonymity for password checking</li>
                <li>🔒 Rate limiting + Input validation</li>
              </ul>
            </div>
          </div>

          {/* System Metrics */}
          <div className="mt-8 bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-8 rounded-xl shadow-lg">
            <h3 className="text-2xl font-bold text-center mb-6">System Performance Metrics</h3>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div className="bg-white bg-opacity-20 p-4 rounded">
                <div className="text-3xl font-bold">10B+</div>
                <div className="text-sm">Credentials Monitored</div>
              </div>
              <div className="bg-white bg-opacity-20 p-4 rounded">
                <div className="text-3xl font-bold">&lt;24h</div>
                <div className="text-sm">Detection Latency</div>
              </div>
              <div className="bg-white bg-opacity-20 p-4 rounded">
                <div className="text-3xl font-bold">&lt;5min</div>
                <div className="text-sm">Alert Delivery</div>
              </div>
              <div className="bg-white bg-opacity-20 p-4 rounded">
                <div className="text-3xl font-bold">99.5%</div>
                <div className="text-sm">System Uptime</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default FlowChart;