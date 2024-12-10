import { useState, useEffect } from 'react'
import { 
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
  }, [filters.search, filters.country, filters.startDate, filters.endDate, filters.use_keywords])

  useEffect(() => {
    onTotalItemsChange?.(total)
  }, [total, onTotalItemsChange])

  useEffect(() => {
    const fetchItems = async () => {
      try {
        setLoading(true)
        const params = {
          search: filters.search || '',
          start_date: filters.startDate || undefined,
          end_date: filters.endDate || undefined,
          skip: (page - 1) * itemsPerPage,
          limit: itemsPerPage,
          use_keywords: filters.use_keywords,
          user_id: 1, // TODO: Get this from authentication context
        }

        if (filters.country) {
          params.country = filters.country
        }
        
        const response = await axios.get('http://localhost:8000/api/items', { params })
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
    setPage(newPage)
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {[1, 2, 3].map((n) => (
          <Card key={n} sx={{ backgroundColor: '#fff' }}>
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
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        minHeight: 200,
        backgroundColor: '#fff',
        borderRadius: 1,
        p: 3
      }}>
        <Typography color="error">{error}</Typography>
      </Box>
    )
  }

  if (items.length === 0) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        minHeight: 200,
        backgroundColor: '#fff',
        borderRadius: 1,
        p: 3
      }}>
        <Typography color="text.secondary">No se encontraron resultados</Typography>
      </Box>
    )
  }

  return (
    <Stack spacing={2}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {items.map((item) => (
          <Card key={item.id} sx={{ backgroundColor: '#fff' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {item.title}
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  endIcon={<OpenInNewIcon />}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ ml: 2, minWidth: 100 }}
                >
                  Ver
                </Button>
              </Box>
              
              <Typography 
                variant="body2" 
                color="text.secondary" 
                paragraph
                sx={{ 
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  mb: 2
                }}
              >
                {item.description}
              </Typography>

              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  label={format(new Date(item.date), 'dd MMM yyyy', { locale: es })}
                  size="small"
                  sx={{ backgroundColor: '#e3f2fd' }}
                />
                <Chip 
                  label={item.country}
                  size="small"
                  sx={{ backgroundColor: '#e8f5e9' }}
                />
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
        <Pagination
          count={Math.ceil(total / itemsPerPage)}
          page={page}
          onChange={handlePageChange}
          color="primary"
          showFirstButton
          showLastButton
        />
      </Box>
    </Stack>
  )
}

export default ItemList
