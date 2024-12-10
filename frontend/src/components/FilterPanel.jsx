import { useState, useEffect } from 'react'
import { 
  TextField, 
  Box,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  InputAdornment,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
  Chip,
  Stack,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers'
import dayjs from 'dayjs'
import SearchIcon from '@mui/icons-material/Search'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import RefreshIcon from '@mui/icons-material/Refresh'
import axios from 'axios'

const FilterPanel = ({ filters, onFilterChange }) => {
  const [country, setCountry] = useState(filters.country)
  const [isScrapingLoading, setIsScrapingLoading] = useState(false)
  const [scrapingStatus, setScrapingStatus] = useState(null)
  const [scrapingInterval, setScrapingInterval] = useState(null)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })
  const [keywords, setKeywords] = useState([])
  const [newKeyword, setNewKeyword] = useState('')
  const [useKeywords, setUseKeywords] = useState(false)
  const [isLoadingKeywords, setIsLoadingKeywords] = useState(false)

  // Cargar palabras clave al inicio
  useEffect(() => {
    const fetchKeywords = async () => {
      try {
        setIsLoadingKeywords(true)
        // TODO: Obtener user_id del contexto de autenticación
        const userId = 1
        const response = await axios.get(`http://localhost:8000/api/users/${userId}/keywords`)
        const userKeywords = response.data.map(k => k.word)
        setKeywords(userKeywords)
        console.log('Palabras clave cargadas:', userKeywords)
      } catch (error) {
        console.error('Error al cargar palabras clave:', error)
        setSnackbar({
          open: true,
          message: 'Error al cargar palabras clave',
          severity: 'error'
        })
      } finally {
        setIsLoadingKeywords(false)
      }
    }

    fetchKeywords()
  }, [])

  // Limpiar el intervalo cuando el componente se desmonte
  useEffect(() => {
    return () => {
      if (scrapingInterval) {
        clearInterval(scrapingInterval)
      }
    }
  }, [scrapingInterval])

  const handleCountryChange = (event, newCountry) => {
    setCountry(newCountry)
    onFilterChange({ country: newCountry })
  }

  const handleKeywordSubmit = async (event) => {
    event.preventDefault()
    if (!newKeyword.trim()) return

    try {
      // TODO: Obtener user_id del contexto de autenticación
      const userId = 1
      await axios.post(`http://localhost:8000/api/users/${userId}/keywords`, {
        word: newKeyword
      })
      
      setKeywords([...keywords, newKeyword])
      setNewKeyword('')
      setSnackbar({
        open: true,
        message: 'Palabra clave agregada exitosamente',
        severity: 'success'
      })
    } catch (error) {
      console.error('Error al agregar palabra clave:', error)
      setSnackbar({
        open: true,
        message: 'Error al agregar palabra clave',
        severity: 'error'
      })
    }
  }

  const handleKeywordDelete = async (keywordToDelete) => {
    try {
      // TODO: Obtener user_id del contexto de autenticación
      const userId = 1
      await axios.delete(`http://localhost:8000/api/users/${userId}/keywords/${keywordToDelete}`)
      
      const updatedKeywords = keywords.filter(k => k !== keywordToDelete)
      setKeywords(updatedKeywords)
      setSnackbar({
        open: true,
        message: 'Palabra clave eliminada exitosamente',
        severity: 'success'
      })
    } catch (error) {
      console.error('Error al eliminar palabra clave:', error)
      setSnackbar({
        open: true,
        message: 'Error al eliminar palabra clave',
        severity: 'error'
      })
    }
  }

  const handleUseKeywordsChange = (event, newValue) => {
    if (newValue !== null) {
      setUseKeywords(newValue)
      onFilterChange({ use_keywords: newValue })
    }
  }

  const handleStartScraping = async () => {
    try {
      setIsScrapingLoading(true)
      const response = await axios.post('http://localhost:8000/api/scraping')
      setScrapingStatus(response.data)
      
      // Iniciar polling del estado
      const interval = setInterval(async () => {
        try {
          const statusResponse = await axios.get('http://localhost:8000/api/scraping/status')
          setScrapingStatus(statusResponse.data)
          
          // Si el scraping ha terminado, detener el polling
          if (!statusResponse.data.is_running) {
            clearInterval(interval)
            setIsScrapingLoading(false)
            setSnackbar({
              open: true,
              message: 'Scraping completado exitosamente',
              severity: 'success'
            })
          }
        } catch (error) {
          console.error('Error al obtener estado del scraping:', error)
          clearInterval(interval)
          setIsScrapingLoading(false)
          setSnackbar({
            open: true,
            message: 'Error al obtener estado del scraping',
            severity: 'error'
          })
        }
      }, 2000)
      
      setScrapingInterval(interval)
      
    } catch (error) {
      console.error('Error al iniciar scraping:', error)
      setIsScrapingLoading(false)
      setSnackbar({
        open: true,
        message: 'Error al iniciar scraping',
        severity: 'error'
      })
    }
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          País
        </Typography>
        <ToggleButtonGroup
          value={country}
          exclusive
          onChange={handleCountryChange}
          aria-label="country filter"
          size="small"
          sx={{ mb: 2 }}
        >
          <ToggleButton value="Chile" aria-label="Chile">
            Chile
          </ToggleButton>
          <ToggleButton value="Perú" aria-label="Perú">
            Perú
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Rango de Fechas
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <DatePicker
            label="Fecha Inicio"
            value={filters.startDate ? dayjs(filters.startDate) : null}
            onChange={(newValue) => {
              const formattedDate = newValue ? newValue.format('YYYY-MM-DD') : null;
              console.log('Start Date changed:', formattedDate);
              onFilterChange({ startDate: formattedDate });
            }}
            format="DD/MM/YYYY"
            slotProps={{
              textField: {
                size: "small",
                fullWidth: true,
                InputProps: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <CalendarTodayIcon />
                    </InputAdornment>
                  )
                }
              },
              field: {
                clearable: true
              }
            }}
            onClear={() => {
              console.log('Start Date cleared');
              onFilterChange({ startDate: null });
            }}
          />
          <DatePicker
            label="Fecha Fin"
            value={filters.endDate ? dayjs(filters.endDate) : null}
            onChange={(newValue) => {
              const formattedDate = newValue ? newValue.format('YYYY-MM-DD') : null;
              console.log('End Date changed:', formattedDate);
              onFilterChange({ endDate: formattedDate });
            }}
            format="DD/MM/YYYY"
            slotProps={{
              textField: {
                size: "small",
                fullWidth: true,
                InputProps: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <CalendarTodayIcon />
                    </InputAdornment>
                  )
                }
              },
              field: {
                clearable: true
              }
            }}
            onClear={() => {
              console.log('End Date cleared');
              onFilterChange({ endDate: null });
            }}
          />
        </Box>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Palabras Clave
        </Typography>
        <ToggleButtonGroup
          value={useKeywords}
          exclusive
          onChange={handleUseKeywordsChange}
          aria-label="use keywords"
          size="small"
          sx={{ mb: 2 }}
        >
          <ToggleButton value={true} aria-label="Usar">
            Usar
          </ToggleButton>
          <ToggleButton value={false} aria-label="No usar">
            No usar
          </ToggleButton>
        </ToggleButtonGroup>

        <Box component="form" onSubmit={handleKeywordSubmit} sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            size="small"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            placeholder="Nueva palabra clave"
            fullWidth
          />
          <Button
            variant="contained"
            type="submit"
            disabled={!newKeyword.trim()}
          >
            Agregar
          </Button>
        </Box>

        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {keywords.map((keyword, index) => (
            <Chip
              key={index}
              label={keyword}
              onDelete={() => handleKeywordDelete(keyword)}
              sx={{ mb: 1 }}
            />
          ))}
          {isLoadingKeywords && <CircularProgress size={20} />}
        </Stack>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          variant="contained"
          onClick={handleStartScraping}
          disabled={isScrapingLoading}
          startIcon={isScrapingLoading ? <CircularProgress size={20} /> : <RefreshIcon />}
        >
          {isScrapingLoading ? 'Actualizando...' : 'Actualizar Datos'}
        </Button>

        {scrapingStatus && scrapingStatus.is_running && (
          <Typography variant="body2" color="text.secondary">
            Progreso: {scrapingStatus.completed_sources}/{scrapingStatus.total_sources}
          </Typography>
        )}
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default FilterPanel
