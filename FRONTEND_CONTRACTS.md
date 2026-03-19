# 🎨 Frontend API Contracts & Integration Guide

This document provides the complete API contract specification for frontend development, aligned with the TMS backend implementation.

## 📡 Standard API Response Format

All API responses follow this consistent format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

**Error Response Format:**
```json
{
  "success": false,
  "data": null,
  "error": "Error message description"
}
```

## 🔌 API Endpoints for Frontend Integration

### 📊 Dashboard & KPIs

**GET** `/loads/kpis/dashboard`
```json
{
  "success": true,
  "data": {
    "total_loads": 150,
    "pending_loads": 25,
    "assigned_loads": 45,
    "in_transit_loads": 30,
    "delivered_loads": 40,
    "cancelled_loads": 10
  }
}
```

### 📦 Loads Management

#### Create Load
**POST** `/loads`
```json
// Request
{
  "origin": "New York, NY",
  "destination": "Los Angeles, CA",
  "price": 2500.00,
  "carrier_id": null
}

// Response
{
  "success": true,
  "data": {
    "load": {
      "id": 1,
      "origin": "New York, NY",
      "destination": "Los Angeles, CA",
      "status": "pending",
      "carrier_id": null,
      "price": 2500.00,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### List Loads
**GET** `/loads?status=pending&carrier_id=1&page=1&limit=50`
```json
{
  "success": true,
  "data": {
    "loads": [
      {
        "id": 1,
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "status": "pending",
        "carrier_id": null,
        "price": 2500.00,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 50
  }
}
```

#### Get Load Details
**GET** `/loads/{id}`
```json
{
  "success": true,
  "data": {
    "load": {
      "id": 1,
      "origin": "New York, NY",
      "destination": "Los Angeles, CA",
      "status": "assigned",
      "carrier_id": 1,
      "price": 2500.00,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

#### Update Load Status
**PATCH** `/loads/{id}/status`
```json
// Request
{
  "status": "in_transit"
}

// Response
{
  "success": true,
  "data": {
    "load": {
      "id": 1,
      "origin": "New York, NY",
      "destination": "Los Angeles, CA",
      "status": "in_transit",
      "carrier_id": 1,
      "price": 2500.00,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  }
}
```

#### Assign Carrier
**POST** `/loads/{id}/assign`
```json
// Request
{
  "carrier_id": 1
}

// Response
{
  "success": true,
  "data": {
    "load": {
      "id": 1,
      "origin": "New York, NY",
      "destination": "Los Angeles, CA",
      "status": "assigned",
      "carrier_id": 1,
      "price": 2500.00,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

### 💰 Quotes Management

#### Create Quote
**POST** `/quotes`
```json
// Request
{
  "load_id": 1,
  "carrier_id": 1,
  "rate": 2400.00,
  "estimated_delivery_days": 3,
  "notes": "Express delivery available"
}

// Response
{
  "success": true,
  "data": {
    "quote": {
      "id": 1,
      "load_id": 1,
      "carrier_id": 1,
      "rate": 2400.00,
      "estimated_delivery_days": 3,
      "notes": "Express delivery available",
      "created_at": "2024-01-15T11:15:00Z",
      "updated_at": "2024-01-15T11:15:00Z"
    }
  }
}
```

#### Get Quotes for Load
**GET** `/quotes?load_id=1`
```json
{
  "success": true,
  "data": {
    "quotes": [
      {
        "id": 1,
        "load_id": 1,
        "carrier_id": 1,
        "rate": 2400.00,
        "estimated_delivery_days": 3,
        "notes": "Express delivery available",
        "created_at": "2024-01-15T11:15:00Z",
        "updated_at": "2024-01-15T11:15:00Z"
      }
    ],
    "total": 1
  }
}
```

#### Select Quote & Assign Carrier
**POST** `/quotes/{id}/select`
```json
// Request
{
  "quote_id": 1
}

// Response
{
  "success": true,
  "data": {
    "message": "Quote selected and carrier assigned successfully",
    "load": {
      "id": 1,
      "status": "assigned",
      "carrier_id": 1
    },
    "quote": {
      "id": 1,
      "rate": 2400.00,
      "carrier_id": 1
    }
  }
}
```

### 🚚 Carriers Management

#### Create Carrier
**POST** `/carriers`
```json
// Request
{
  "name": "Fast Freight Inc.",
  "mc_number": "MC123456",
  "phone": "+1-555-0123",
  "email": "contact@fastfreight.com"
}

// Response
{
  "success": true,
  "data": {
    "carrier": {
      "id": 1,
      "name": "Fast Freight Inc.",
      "mc_number": "MC123456",
      "phone": "+1-555-0123",
      "email": "contact@fastfreight.com",
      "created_at": "2024-01-15T09:00:00Z",
      "updated_at": "2024-01-15T09:00:00Z"
    }
  }
}
```

#### List Carriers
**GET** `/carriers?search=Fast&page=1&limit=50`
```json
{
  "success": true,
  "data": {
    "carriers": [
      {
        "id": 1,
        "name": "Fast Freight Inc.",
        "mc_number": "MC123456",
        "phone": "+1-555-0123",
        "email": "contact@fastfreight.com",
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": "2024-01-15T09:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 50
  }
}
```

### 📍 Tracking & Timeline

#### Update Tracking
**POST** `/tracking/update`
```json
// Request
{
  "load_id": 1,
  "status": "In Transit - Chicago Hub",
  "location": "Chicago, IL",
  "notes": "On schedule, no delays"
}

// Response
{
  "success": true,
  "data": {
    "tracking_event": {
      "id": 1,
      "load_id": 1,
      "status": "In Transit - Chicago Hub",
      "location": "Chicago, IL",
      "notes": "On schedule, no delays",
      "timestamp": "2024-01-15T16:45:00Z"
    },
    "message": "Tracking event added successfully"
  }
}
```

#### Get Tracking Timeline
**GET** `/tracking/{load_id}`
```json
{
  "success": true,
  "data": {
    "load_id": 1,
    "events": [
      {
        "id": 2,
        "status": "In Transit - Chicago Hub",
        "location": "Chicago, IL",
        "notes": "On schedule, no delays",
        "timestamp": "2024-01-15T16:45:00Z"
      },
      {
        "id": 1,
        "status": "Picked Up",
        "location": "New York, NY",
        "notes": "Load picked up from warehouse",
        "timestamp": "2024-01-15T12:00:00Z"
      }
    ],
    "total_events": 2
  }
}
```

#### Get Latest Tracking
**GET** `/tracking/{load_id}/latest`
```json
{
  "success": true,
  "data": {
    "latest_tracking": {
      "id": 2,
      "status": "In Transit - Chicago Hub",
      "location": "Chicago, IL",
      "notes": "On schedule, no delays",
      "timestamp": "2024-01-15T16:45:00Z"
    },
    "load_id": 1
  }
}
```

### 🎯 Invoice-Contract Matching

#### Match Invoice to Contract
**POST** `/matching/invoice-contract`
```json
// Request
{
  "invoices": [
    {
      "invoice_id": "INV-001",
      "invoice_name": "Fast Freight Transportation Inc."
    }
  ],
  "contracts": [
    {
      "contract_id": "CONTRACT-001",
      "name": "Fast Freight Inc."
    }
  ]
}

// Response
{
  "success": true,
  "data": {
    "matches": [
      {
        "invoice_id": "INV-001",
        "invoice_name": "Fast Freight Transportation Inc.",
        "best_match": "Fast Freight Inc.",
        "similarity_score": 0.85,
        "is_match": true,
        "confidence": "medium"
      }
    ],
    "total_processed": 1,
    "high_confidence_matches": 0,
    "medium_confidence_matches": 1,
    "low_confidence_matches": 0
  }
}
```

## 🎨 Frontend Component Structure

### Dashboard Component
```javascript
// API calls needed:
// GET /loads/kpis/dashboard
// GET /loads?status=pending&limit=10

const Dashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [recentLoads, setRecentLoads] = useState([]);
  
  useEffect(() => {
    fetchKPIs();
    fetchRecentLoads();
  }, []);
};
```

### Loads Table Component
```javascript
// API calls needed:
// GET /loads (with filters)
// PATCH /loads/{id}/status
// POST /loads/{id}/assign

const LoadsTable = () => {
  const [loads, setLoads] = useState([]);
  const [filters, setFilters] = useState({
    status: '',
    carrier_id: null
  });
};
```

### Load Detail Component
```javascript
// API calls needed:
// GET /loads/{id}
// GET /tracking/{id}
// GET /quotes?load_id={id}

const LoadDetail = ({ loadId }) => {
  const [load, setLoad] = useState(null);
  const [tracking, setTracking] = useState([]);
  const [quotes, setQuotes] = useState([]);
};
```

### Quote Comparison Component
```javascript
// API calls needed:
// GET /quotes?load_id={id}
// POST /quotes/{id}/select

const QuoteComparison = ({ loadId }) => {
  const [quotes, setQuotes] = useState([]);
  
  const handleSelectQuote = async (quoteId) => {
    // POST /quotes/{id}/select
  };
};
```

### Tracking Timeline Component
```javascript
// API calls needed:
// GET /tracking/{load_id}
// POST /tracking/update

const TrackingTimeline = ({ loadId }) => {
  const [events, setEvents] = useState([]);
  
  const handleUpdateTracking = async (eventData) => {
    // POST /tracking/update
  };
};
```

## 🔄 State Management Pattern

### Global State Structure
```javascript
const initialState = {
  loads: {
    list: [],
    current: null,
    loading: false,
    error: null
  },
  carriers: {
    list: [],
    current: null,
    loading: false,
    error: null
  },
  quotes: {
    list: [],
    current: null,
    loading: false,
    error: null
  },
  tracking: {
    events: [],
    loading: false,
    error: null
  },
  kpis: {
    data: null,
    loading: false,
    error: null
  }
};
```

### API Response Handler
```javascript
const handleApiResponse = (response) => {
  if (response.success) {
    return response.data;
  } else {
    throw new Error(response.error || 'API request failed');
  }
};
```

## 🚀 Optimistic Updates

For better UX, implement optimistic updates:

```javascript
const updateLoadStatus = async (loadId, newStatus) => {
  // Optimistic update
  setLoads(prev => prev.map(load => 
    load.id === loadId 
      ? { ...load, status: newStatus }
      : load
  ));
  
  try {
    const response = await api.patch(`/loads/${loadId}/status`, { status: newStatus });
    handleApiResponse(response);
  } catch (error) {
    // Rollback on error
    setLoads(prev => prev.map(load => 
      load.id === loadId 
        ? { ...load, status: load.previousStatus }
        : load
    ));
  }
};
```

## 📱 Real-time Features

For real-time updates, consider implementing:

1. **WebSocket Connection** for live tracking updates
2. **Server-Sent Events** for load status changes
3. **Polling** as fallback for dashboard KPIs

```javascript
// WebSocket example for real-time tracking
const ws = new WebSocket('ws://localhost:8000/ws/tracking');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'tracking_update') {
    updateTrackingEvent(data.payload);
  }
};
```

## 🎯 UX Requirements Implementation

### Minimal Clicks
- Quick action buttons on load cards
- Bulk operations for status updates
- Keyboard shortcuts for common actions

### Real-time Feel
- Optimistic updates
- Loading states
- Progress indicators
- Toast notifications for actions

### Responsive Design
- Mobile-first approach
- Touch-friendly interfaces
- Adaptive layouts for different screen sizes

This contract provides everything needed for frontend developers to build a complete, production-ready TMS interface that seamlessly integrates with the backend API.
