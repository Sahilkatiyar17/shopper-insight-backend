
import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { ChevronDown, ChevronUp, RefreshCw } from "lucide-react";

interface Customer {
  customer_id: string;
  full_name: string;
  email: string;
  username: string;
  phone_number: string;
  age: number;
  gender: string;
  location: string;
}

interface Product {
  product_id: number;
  product_name: string;
  category: string;
  price: number;
  score: number;
}

interface Recommendation {
  customer_id: string;
  recommendations: Product[];
  timestamp?: string;
}

const TestCustomers: Customer[] = [
  {
    customer_id: "tech001",
    full_name: "Alex Tech",
    email: "alex@example.com",
    username: "alextech",
    phone_number: "1234567890",
    age: 28,
    gender: "Male",
    location: "California"
  },
  {
    customer_id: "fitness001",
    full_name: "Fiona Fit",
    email: "fiona@example.com",
    username: "fionafit",
    phone_number: "2345678901",
    age: 32,
    gender: "Female",
    location: "Colorado"
  },
  {
    customer_id: "fashion001",
    full_name: "Maya Style",
    email: "maya@example.com",
    username: "mayastyle",
    phone_number: "3456789012",
    age: 24,
    gender: "Female",
    location: "New York"
  }
];

const Index = () => {
  const { toast } = useToast();
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [serverRunning, setServerRunning] = useState(false);
  const [browsingCategory, setBrowsingCategory] = useState("");
  const [activeCustomers, setActiveCustomers] = useState<{[key: string]: boolean}>({});

  // Check if server is running on component mount
  useEffect(() => {
    checkServerStatus();
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/docs", { method: "HEAD" });
      setServerRunning(response.ok);
    } catch (error) {
      setServerRunning(false);
    }
  };

  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setRecommendations([]);
    
    // Toggle customer dropdown
    setActiveCustomers({
      ...activeCustomers,
      [customer.customer_id]: !activeCustomers[customer.customer_id]
    });
    
    // Get recommendations if dropdown is opening
    if (!activeCustomers[customer.customer_id]) {
      getRecommendations(customer.customer_id);
    }
  };

  const createTestCustomer = async (customer: Customer) => {
    if (!serverRunning) {
      toast({
        title: "Server Error",
        description: "The recommendation server is not running. Please start it with 'python main.py'",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/customer/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(customer)
      });

      if (response.ok) {
        toast({
          title: "Customer Created",
          description: `Successfully created customer: ${customer.full_name}`
        });
      } else {
        const error = await response.json();
        toast({
          title: "Error Creating Customer",
          description: error.detail || "Unknown error",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Connection Error",
        description: "Failed to connect to the server. Is it running?",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async (customerId: string) => {
    if (!serverRunning) {
      toast({
        title: "Server Error",
        description: "The recommendation server is not running. Please start it with 'python main.py'",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/recommendations/${customerId}`);
      if (response.ok) {
        const data: Recommendation = await response.json();
        setRecommendations(data.recommendations);
        toast({
          title: "Recommendations Retrieved",
          description: `Found ${data.recommendations.length} recommendations for this customer`
        });
      } else {
        const error = await response.json();
        toast({
          title: "Error Getting Recommendations",
          description: error.detail || "Unknown error",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Connection Error",
        description: "Failed to connect to the server. Is it running?",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const addBrowsingHistory = async () => {
    if (!selectedCustomer || !browsingCategory) {
      toast({
        title: "Missing Information",
        description: "Please select a customer and enter a browsing category",
        variant: "destructive"
      });
      return;
    }

    if (!serverRunning) {
      toast({
        title: "Server Error",
        description: "The recommendation server is not running. Please start it with 'python main.py'",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/customer/update-behavior", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: selectedCustomer.customer_id,
          browsing_category: browsingCategory
        })
      });

      if (response.ok) {
        toast({
          title: "Browsing History Added",
          description: `Added ${browsingCategory} to browsing history`
        });
        // Get updated recommendations
        getRecommendations(selectedCustomer.customer_id);
        setBrowsingCategory("");
      } else {
        const error = await response.json();
        toast({
          title: "Error Adding Browsing History",
          description: error.detail || "Unknown error",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Connection Error",
        description: "Failed to connect to the server. Is it running?",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Recommendation System Tester</h1>
      
      {!serverRunning && (
        <Card className="mb-6 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-600">Server Not Running</CardTitle>
          </CardHeader>
          <CardContent>
            <p>The recommendation server is not running. Please start it by running:</p>
            <pre className="bg-gray-100 p-3 my-2 rounded">python src/main.py</pre>
            <p>Then click the button below to check if the server is up:</p>
          </CardContent>
          <CardFooter>
            <Button onClick={checkServerStatus} variant="outline" className="mt-2">
              <RefreshCw className="mr-2 h-4 w-4" />
              Check Server Status
            </Button>
          </CardFooter>
        </Card>
      )}

      <Tabs defaultValue="test" className="mt-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="test">Test Recommendations</TabsTrigger>
          <TabsTrigger value="create">Create Test Data</TabsTrigger>
        </TabsList>
        
        <TabsContent value="test" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Customer Recommendations</CardTitle>
              <CardDescription>
                Select a customer to view their personalized product recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {TestCustomers.map((customer) => (
                  <div key={customer.customer_id} className="border rounded-lg overflow-hidden">
                    <div 
                      className="flex justify-between items-center p-4 cursor-pointer bg-gray-50 hover:bg-gray-100"
                      onClick={() => handleSelectCustomer(customer)}
                    >
                      <div>
                        <h3 className="font-medium">{customer.full_name}</h3>
                        <p className="text-sm text-gray-500">{customer.customer_id} - {customer.location}</p>
                      </div>
                      <div>
                        {activeCustomers[customer.customer_id] ? 
                          <ChevronUp className="h-5 w-5" /> : 
                          <ChevronDown className="h-5 w-5" />
                        }
                      </div>
                    </div>
                    
                    {activeCustomers[customer.customer_id] && (
                      <div className="p-4 border-t">
                        {selectedCustomer?.customer_id === customer.customer_id && recommendations.length > 0 ? (
                          <div className="space-y-3">
                            <h4 className="font-medium mb-2">Product Recommendations:</h4>
                            {recommendations.map((product, idx) => (
                              <div key={idx} className="flex justify-between items-center p-3 bg-white rounded border">
                                <div>
                                  <p className="font-medium">{product.product_name}</p>
                                  <p className="text-sm text-gray-500">Category: {product.category}</p>
                                </div>
                                <div className="text-right">
                                  <p className="font-medium">${product.price.toFixed(2)}</p>
                                  <p className="text-sm text-gray-500">Score: {product.score.toFixed(4)}</p>
                                </div>
                              </div>
                            ))}
                            
                            <div className="mt-4 pt-4 border-t">
                              <Label htmlFor="browsing-category">Add Browsing Activity:</Label>
                              <div className="flex gap-2 mt-2">
                                <Input
                                  id="browsing-category"
                                  placeholder="e.g., Laptop, Yoga, fashion"
                                  value={browsingCategory}
                                  onChange={(e) => setBrowsingCategory(e.target.value)}
                                />
                                <Button 
                                  onClick={addBrowsingHistory}
                                  disabled={loading || !browsingCategory}
                                >
                                  Add
                                </Button>
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                Add browsing data to see how recommendations change
                              </p>
                            </div>
                          </div>
                        ) : loading ? (
                          <p className="text-center py-4">Loading recommendations...</p>
                        ) : (
                          <div className="text-center py-4">
                            <p>No recommendations found</p>
                            <Button 
                              onClick={() => getRecommendations(customer.customer_id)}
                              variant="outline"
                              className="mt-2"
                            >
                              Get Recommendations
                            </Button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="create" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Create Test Data</CardTitle>
              <CardDescription>
                Create test customers to generate recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {TestCustomers.map((customer) => (
                <div key={customer.customer_id} className="p-4 border rounded-lg">
                  <h3 className="font-medium">{customer.full_name}</h3>
                  <p className="text-sm text-gray-500 mb-3">
                    {customer.customer_id} - {customer.gender}, {customer.age} - {customer.location}
                  </p>
                  <Button 
                    onClick={() => createTestCustomer(customer)}
                    variant="outline"
                    disabled={loading}
                  >
                    Create Customer
                  </Button>
                </div>
              ))}
            </CardContent>
            <CardFooter>
              <Button 
                onClick={() => {
                  TestCustomers.forEach(customer => createTestCustomer(customer));
                }}
                disabled={loading}
                className="w-full"
              >
                Create All Test Customers
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Run Full Evaluation</CardTitle>
          <CardDescription>
            Run the full evaluation script to test the recommendation system accuracy
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-4">
            The evaluation script will:
          </p>
          <ul className="list-disc pl-5 space-y-1 mb-4">
            <li>Create multiple test customers with different profiles</li>
            <li>Add browsing and purchase history for each customer</li>
            <li>Generate recommendations for each customer</li>
            <li>Evaluate the quality of the recommendations</li>
            <li>Calculate a relevance score for each customer</li>
            <li>Provide an overall system performance rating</li>
          </ul>
          <p className="text-sm bg-gray-100 p-3 rounded">
            Run this command in your terminal to start the evaluation:
            <br />
            <code className="font-mono">python src/run_evaluation.py</code>
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Index;
