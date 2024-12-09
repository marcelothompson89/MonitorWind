import { useState, useEffect } from 'react'
import { 
  Paper,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Chip,
  CircularProgress,
  Skeleton,
  Pagination,
  Stack,
} from '@mui/material'
import axios from 'axios'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'

const ItemList = ({ filters, onTotalItemsChange }) => {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const itemsPerPage = 10

  useEffect(() => {
    setPage(1) // Reset to first page when filters change
  }, [filters.search, filters.country, filters.startDate, filters.endDate, filters.source_type, filters.use_keywords, filters.keywords])

  useEffect(() => {
    onTotalItemsChange?.(total)
  }, [total, onTotalItemsChange])

  useEffect(() => {
    const fetchItems = async () => {
      try {
        setLoading(true)
        const params = {
          search: filters.search || '',
          start_date: filters.startDate ? format(filters.startDate, 'yyyy-MM-dd') : undefined,
          end_date: filters.endDate ? format(filters.endDate, 'yyyy-MM-dd') : undefined,
          skip: (page - 1) * itemsPerPage,
          limit: itemsPerPage,
          use_keywords: filters.use_keywords,
          user_id: 1, // TODO: Get this from authentication context
        }

        // Only add country parameter if it's not "TODOS"
        if (filters.country && filters.country !== "TODOS") {
          params.country = filters.country;
        }

        // Only add source_type parameter if it's not empty
        if (filters.source_type) {
          params.source_type = filters.source_type;
        }
        
        console.log('Sending request with params:', params);
        const response = await axios.get('http://localhost:8000/api/items', { params })
        console.log('Received response:', response.data);
        setItems(response.data.items)
        setTotal(response.data.total)
        setError(null)
      } catch (err) {
        setError('Error al cargar los items')
        console.error('Error fetching items:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchItems()
  }, [filters, page])

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {[1, 2, 3].map((n) => (
          <Card key={n}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Skeleton variant="text" width="60%" height={32} />
                <Skeleton variant="rectangular" width={60} height={24} />
              </Box>
              <Skeleton variant="text" width="90%" />
              <Skeleton variant="text" width="40%" />
            </CardContent>
          </Card>
        ))}
      </Box>
    )
  }

  if (error) {
    return (
      <Paper 
        sx={{ 
          p: 3, 
          textAlign: 'center', 
          color: 'error.main',
          backgroundColor: 'error.light',
          borderRadius: 2
        }}
      >
        {error}
      </Paper>
    )
  }

  if (items.length === 0) {
    return (
      <Paper 
        sx={{ 
          p: 4, 
          textAlign: 'center',
          borderRadius: 2,
          backgroundColor: 'grey.50'
        }}
      >
        <Typography variant="h6" color="text.secondary">
          No se encontraron resultados
        </Typography>
      </Paper>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {items.map((item) => (
        <Card 
          key={item.id}
          sx={{ 
            borderRadius: 2,
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {item.title}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <Chip 
                    label={item.source_name} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                  <Chip 
                    label={item.country} 
                    size="small" 
                    color="secondary" 
                    variant="outlined"
                  />
                  <Typography variant="body2" color="text.secondary">
                    {format(new Date(item.presentation_date), 'dd/MM/yyyy', { locale: es })}
                  </Typography>
                </Box>
              </Box>
              <Button 
                size="small"
                variant="outlined"
                href={item.source_url}
                target="_blank"
                rel="noopener noreferrer"
                startIcon={<OpenInNewIcon />}
                sx={{ ml: 2 }}
              >
                Ver fuente
              </Button>
            </Box>
            <Typography variant="body2" color="text.secondary" paragraph>
              {item.description}
            </Typography>
          </CardContent>
        </Card>
      ))}
      
      {/* Pagination controls */}
      {total > itemsPerPage && (
        <Stack spacing={2} alignItems="center" sx={{ mt: 3 }}>
          <Pagination
            count={Math.ceil(total / itemsPerPage)}
            page={page}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
            size="large"
          />
        </Stack>
      )}
    </Box>
  )
}

export default ItemList
