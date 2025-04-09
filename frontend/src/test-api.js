import { featureApi } from './services/api';

// Test function to check all GET endpoints
async function testApiEndpoints() {
  console.log('Testing API endpoints...');
  
  try {
    // Test GET /features
    console.log('\nTesting GET /features:');
    const features = await featureApi.getFeatures();
    console.log('Features:', features);
    
    // Test GET /sql/sets
    console.log('\nTesting GET /sql/sets:');
    const sqlSets = await featureApi.getSqlSets();
    console.log('SQL Sets:', sqlSets);
    
    // Test GET /sql/statements
    console.log('\nTesting GET /sql/statements:');
    const sqlStatements = await featureApi.getSqlStatements();
    console.log('SQL Statements:', sqlStatements);
    
    console.log('\nAll API tests completed successfully!');
  } catch (error) {
    console.error('API test failed:', error);
    console.error('Error details:', error.response?.data || error.message);
  }
}

// Run the tests
testApiEndpoints(); 