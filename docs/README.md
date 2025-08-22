# Portfolio Manager Documentation

Welcome to the comprehensive documentation for Portfolio Manager - a modern web-based stock portfolio management and rebalancing application.

## 📚 Documentation Overview

This documentation covers everything you need to know about Portfolio Manager, from basic usage to advanced deployment and development.

### Quick Start
- New users: Start with the [User Guide](user-guide.md)
- Developers: Check out the [Developer Guide](developer-guide.md)
- API integration: See the [API Reference](api-reference.md)

## 📖 Available Documentation

### [📋 User Guide](user-guide.md)
**Complete guide for end users**
- Getting started and first-time setup
- Portfolio and watchlist management
- Market news features
- Stock price management
- CSV import/export
- Tips and best practices

### [🛠 Developer Guide](developer-guide.md)
**Comprehensive development documentation**
- Development environment setup
- Project architecture and code structure
- Testing framework and best practices
- API development guidelines
- Frontend development with FastAPI templates
- Database management with SQLAlchemy
- Contributing guidelines

### [🔌 API Reference](api-reference.md)
**Complete API documentation**
- Authentication and response formats
- Portfolio management endpoints
- Holdings and stock data endpoints
- Watchlist management endpoints
- Market news integration endpoints
- Error handling and rate limiting
- SDK examples for Python and JavaScript

### [🚀 Deployment Guide](deployment.md)
**Deployment and configuration**
- Local development setup
- Production deployment options
- Docker containerization
- Environment configuration
- Security considerations
- Performance optimization
- Monitoring and logging
- Backup and recovery procedures

### [🔧 Troubleshooting Guide](troubleshooting.md)
**Common issues and solutions**
- Installation and startup problems
- Database and API issues
- News integration troubleshooting
- Performance optimization
- Browser and UI problems
- Getting help and support

## 🏗 Project Architecture

### High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (HTML/JS/CSS) │◄──►│   (FastAPI)     │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       └─────────────────┘
```

### Key Components

- **FastAPI Backend**: RESTful API with automatic documentation
- **SQLAlchemy ORM**: Database models and relationships
- **Bootstrap Frontend**: Responsive web interface
- **Multi-source News**: Polygon.io, Yahoo Finance, and fallback options
- **Real-time Data**: Stock prices with intelligent caching
- **Local Storage**: SQLite database for privacy and speed

## 🚀 Quick Navigation

### For Users
1. **Installation**: [User Guide > Getting Started](user-guide.md#getting-started)
2. **Create Portfolio**: [User Guide > Portfolio Management](user-guide.md#portfolio-management)
3. **Add Stocks**: [User Guide > Adding Holdings](user-guide.md#adding-holdings-manually)
4. **View News**: [User Guide > Market News](user-guide.md#market-news-features)
5. **Troubleshooting**: [Troubleshooting Guide](troubleshooting.md)

### For Developers
1. **Setup Environment**: [Developer Guide > Setup](developer-guide.md#development-environment-setup)
2. **Project Structure**: [Developer Guide > Code Structure](developer-guide.md#code-structure)
3. **API Development**: [Developer Guide > API Development](developer-guide.md#api-development)
4. **Testing**: [Developer Guide > Testing](developer-guide.md#testing)
5. **Contributing**: [Developer Guide > Contributing](developer-guide.md#contributing-guidelines)

### For Deployment
1. **Local Deployment**: [Deployment Guide > Local Setup](deployment.md#local-development-setup)
2. **Production Setup**: [Deployment Guide > Production](deployment.md#production-deployment)
3. **Docker**: [Deployment Guide > Docker](deployment.md#docker-deployment)
4. **Security**: [Deployment Guide > Security](deployment.md#security-considerations)
5. **Monitoring**: [Deployment Guide > Monitoring](deployment.md#monitoring-and-logging)

## 📋 Feature Documentation

### Core Features (Completed)
- ✅ **Portfolio Management**: Multiple named portfolios with target allocations
- ✅ **Holdings Management**: Add, edit, delete stock holdings
- ✅ **CSV Import/Export**: Bulk operations with validation
- ✅ **Real-time Prices**: Yahoo Finance integration with caching
- ✅ **Watchlist System**: Track stocks without owning them
- ✅ **Market News**: Multi-source news with Polygon.io and Yahoo Finance
- ✅ **Responsive UI**: Bootstrap-based interface for all devices
- ✅ **Data Validation**: Comprehensive input validation and error handling

### Upcoming Features
- 🔄 **Portfolio Rebalancing**: Automated buy/sell recommendations
- 📊 **Advanced Charts**: Interactive price and performance charts
- 📈 **Performance Analytics**: Risk metrics and diversification analysis
- 📑 **Enhanced Reporting**: PDF exports and detailed analytics

## 🔗 External Resources

### APIs and Data Sources
- [Yahoo Finance API](https://finance.yahoo.com) - Primary stock data source
- [Polygon.io](https://polygon.io) - Premium news and market data (optional)
- [FastAPI Documentation](https://fastapi.tiangolo.com) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org) - Database ORM

### Related Tools
- [uv Package Manager](https://docs.astral.sh/uv/) - Python package management
- [Bootstrap 5](https://getbootstrap.com) - CSS framework
- [Docker](https://www.docker.com) - Containerization platform

## 🤝 Contributing

We welcome contributions! Please see the [Developer Guide > Contributing Guidelines](developer-guide.md#contributing-guidelines) for:

- Code standards and style guide
- Pull request process
- Issue reporting guidelines
- Development workflow

## 📄 License

This project is designed for educational and personal use. Please check the license file for specific terms and conditions.

## 📞 Support

### Getting Help

1. **Check Documentation**: Browse this comprehensive documentation
2. **Search Issues**: Look through existing GitHub issues
3. **Troubleshooting**: Review the [Troubleshooting Guide](troubleshooting.md)
4. **Create Issue**: Submit detailed bug reports or feature requests

### Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Pull Requests**: Code contributions and improvements

---

## 📚 Documentation Maintenance

This documentation is maintained alongside the codebase. When contributing:

- Update relevant documentation with code changes
- Add new sections for new features
- Keep examples current and tested
- Follow the established documentation style

**Last Updated**: January 6, 2025  
**Documentation Version**: 1.0  
**Application Version**: 1.0 (Sprints 1-5 completed)