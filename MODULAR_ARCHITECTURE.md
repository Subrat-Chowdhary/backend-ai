# 🏗️ Modular Query Enhancement Architecture

## 🎯 Overview

This architecture provides a **lightweight backend** with **modular query enhancement** capabilities. You can start with a minimal setup and add AI-powered query enhancement later without changing your core application.

## 🚀 Quick Start (Lightweight)

### 1. Stop Current Heavy Build
```bash
# Stop the current heavy build
docker compose -f docker-compose.mvp.yml down
```

### 2. Start Lightweight Version
```bash
# Build and start lightweight version (< 1 minute build time!)
docker compose -f docker-compose.light.yml up --build -d
```

### 3. Verify Services
```bash
# Check status
docker compose -f docker-compose.light.yml ps

# Test API
curl http://localhost:8000/health

# Check enhancement status
curl http://localhost:8000/enhancement/status
```

## 📊 Size Comparison

| Version | Build Time | Image Size | Memory Usage | Dependencies |
|---------|------------|------------|--------------|--------------|
| **Heavy (MVP)** | ~10-15 min | ~6GB | ~2GB RAM | PyTorch, CUDA, cuDNN |
| **Light** | ~30-60 sec | ~200MB | ~100MB RAM | Essential only |

## 🔧 Query Enhancement Strategies

### 1. **None** (Default - Instant)
```bash
# No enhancement - returns original query
curl -X POST "http://localhost:8000/enhancement/configure" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "none"}'
```

### 2. **OpenAI** (Recommended for Production)
```bash
# Set environment variable
export OPENAI_API_KEY="your-api-key"

# Configure strategy
curl -X POST "http://localhost:8000/enhancement/configure" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "openai"}'

# Test enhancement
curl -X POST "http://localhost:8000/enhancement/enhance" \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer", "context": {"job_category": "Backend"}}'
```

### 3. **Custom API** (Your Own Enhancement Service)
```bash
# Set your custom API endpoint
export CUSTOM_ENHANCER_URL="http://your-llm-service.com/enhance"

# Configure strategy
curl -X POST "http://localhost:8000/enhancement/configure" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "custom_api"}'
```

### 4. **Local LLM** (Add Heavy Dependencies Later)
```bash
# Add to requirements-light.txt:
# sentence-transformers==5.0.0

# Rebuild with local LLM support
docker compose -f docker-compose.light.yml build --no-cache

# Configure strategy
curl -X POST "http://localhost:8000/enhancement/configure" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "local_llm"}'
```

## 🔄 Runtime Strategy Switching

Switch enhancement strategies without restarting:

```bash
# Check current strategy
curl http://localhost:8000/enhancement/status

# Switch to OpenAI
curl -X POST "http://localhost:8000/enhancement/configure" \
  -d '{"strategy": "openai"}'

# Switch back to none
curl -X POST "http://localhost:8000/enhancement/configure" \
  -d '{"strategy": "none"}'
```

## 🧪 Testing Enhancement Strategies

```bash
# Test different strategies with sample queries
curl "http://localhost:8000/enhancement/test/openai?query=Java%20developer%20with%20Spring"
curl "http://localhost:8000/enhancement/test/none?query=Java%20developer%20with%20Spring"

# Compare results
curl http://localhost:8000/enhancement/strategies
```

## 🏗️ Architecture Benefits

### ✅ **Modular Design**
- Start lightweight, add features later
- No vendor lock-in
- Easy to test different strategies

### ✅ **Performance Options**
- **Fast**: No enhancement (instant)
- **Smart**: API-based enhancement (1-2s)
- **Powerful**: Local LLM (2-5s, no API costs)

### ✅ **Cost Optimization**
- Pay only for what you use
- Switch between free and paid options
- Scale based on needs

### ✅ **Development Friendly**
- Fast builds and deployments
- Easy debugging
- Hot-swappable strategies

## 🔧 Configuration Files

### Environment Variables (.env)
```bash
# Copy example and customize
cp .env.example .env

# Edit configuration
QUERY_ENHANCEMENT_STRATEGY=openai
OPENAI_API_KEY=your-key-here
```

### Docker Compose Options
- `docker-compose.light.yml` - Lightweight version
- `docker-compose.mvp.yml` - Heavy ML version (if needed)

## 📈 Migration Path

### Phase 1: Start Light
```bash
docker compose -f docker-compose.light.yml up -d
```

### Phase 2: Add API Enhancement
```bash
# Configure OpenAI or custom API
export OPENAI_API_KEY="your-key"
curl -X POST "http://localhost:8000/enhancement/configure" -d '{"strategy": "openai"}'
```

### Phase 3: Add Local LLM (Optional)
```bash
# Add heavy dependencies to requirements-light.txt
# sentence-transformers==5.0.0

# Rebuild
docker compose -f docker-compose.light.yml build --no-cache
```

## 🎯 Best Practices

### For Development
- Use `strategy: "none"` for fast iteration
- Test with `strategy: "openai"` occasionally

### For Production
- Use `strategy: "openai"` or `strategy: "custom_api"`
- Monitor API costs and performance
- Have fallback to `strategy: "none"`

### For High Volume
- Consider `strategy: "local_llm"` to avoid API costs
- Cache enhanced queries
- Use custom API with your own models

## 🔍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enhancement/status` | GET | Current strategy status |
| `/enhancement/configure` | POST | Change strategy |
| `/enhancement/enhance` | POST | Enhance a query |
| `/enhancement/test/{strategy}` | GET | Test a strategy |
| `/enhancement/strategies` | GET | List all strategies |

## 🚀 Next Steps

1. **Start with lightweight version**
2. **Test basic functionality**
3. **Add query enhancement when needed**
4. **Scale based on requirements**

This modular approach gives you the flexibility to start simple and grow sophisticated as your needs evolve!