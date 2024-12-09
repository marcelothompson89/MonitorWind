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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  OutlinedInput,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers'
import SearchIcon from '@mui/icons-material/Search'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import RefreshIcon from '@mui/icons-material/Refresh'
import axios from 'axios'

const FilterPanel = ({ filters, onFilterChange }) => {
  const [country, setCountry] = useState(filters.country)
  const [sources, setSources] = useState([])
  const [selectedSources, setSelectedSources] = useState([])
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

  // Cargar fuentes al inicio
  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/sources')
        setSources(response.data)
      } catch (error) {
        console.error('Error al cargar fuentes:', error)
        setSnackbar({
          open: true,
          message: 'Error al cargar fuentes',
          severity: 'error'
        })
      }
    }
    fetchSources()
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

  const handleSourceChange = (event) => {
    const value = event.target.value
    setSelectedSources(value)
    onFilterChange({ source_type: value.map(source => source.scraper_type).join(',') })
  }

  // Función para verificar el estado del scraping
  const checkScrapingStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/scraping/status')
      const status = response.data
      setScrapingStatus(status)
      
      if (!status.is_running) {
        // Si el scraping terminó, limpiar el intervalo y actualizar la UI
        if (scrapingInterval) {
          clearInterval(scrapingInterval)
          setScrapingInterval(null)
        }
        setIsScrapingLoading(false)
        
        // Mostrar mensaje de finalización
        const successCount = status.results.filter(r => r.status === 'success').length
        const errorCount = status.results.filter(r => r.status === 'error').length
        setSnackbar({
          open: true,
          message: `Scraping completado. ${successCount} fuentes procesadas exitosamente, ${errorCount} con errores.`,
          severity: 'success',
          autoHideDuration: 6000
        })
        
        // Refrescar los resultados una sola vez al terminar
        onFilterChange({ ...filters })
        return true // Indica que el scraping ha terminado
      }
      return false // Indica que el scraping sigue en proceso
    } catch (error) {
      console.error('Error al verificar estado del scraping:', error)
      // En caso de error, también detenemos el intervalo
      if (scrapingInterval) {
        clearInterval(scrapingInterval)
        setScrapingInterval(null)
      }
      setIsScrapingLoading(false)
      return true
    }
  }

  const handleScrapeAll = async () => {
    try {
      // Si ya hay un proceso en curso, no iniciamos otro
      if (isScrapingLoading) {
        return
      }

      setIsScrapingLoading(true)
      const response = await axios.post('http://localhost:8000/api/scraping/')
      
      // Limpiar cualquier intervalo existente antes de crear uno nuevo
      if (scrapingInterval) {
        clearInterval(scrapingInterval)
      }
      
      // Iniciar el monitoreo del estado
      const intervalId = setInterval(async () => {
        const finished = await checkScrapingStatus()
        if (finished) {
          clearInterval(intervalId)
          setScrapingInterval(null)
        }
      }, 2000)
      setScrapingInterval(intervalId)
      
      setSnackbar({
        open: true,
        message: 'Proceso de scraping iniciado. Por favor espere...',
        severity: 'info',
        autoHideDuration: 3000
      })
    } catch (error) {
      setIsScrapingLoading(false)
      setSnackbar({
        open: true,
        message: 'Error al ejecutar el scraping. Por favor intente nuevamente.',
        severity: 'error',
        autoHideDuration: 6000
      })
      console.error('Error en scraping:', error)
    }
  }

  const handleAddKeyword = async () => {
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      try {
        // TODO: Obtener user_id del contexto de autenticación
        const userId = 1
        await axios.post(`http://localhost:8000/api/users/${userId}/keywords/`, {
          word: newKeyword.trim()
        })
        
        const updatedKeywords = [...keywords, newKeyword.trim()]
        setKeywords(updatedKeywords)
        setNewKeyword('')
        onFilterChange({ use_keywords: useKeywords, keywords: updatedKeywords })
      } catch (error) {
        console.error('Error al agregar palabra clave:', error)
        setSnackbar({
          open: true,
          message: 'Error al agregar palabra clave',
          severity: 'error'
        })
      }
    }
  }

  const handleDeleteKeyword = async (keywordToDelete) => {
    try {
      // TODO: Obtener user_id del contexto de autenticación
      const userId = 1
      // Encontrar el ID de la palabra clave
      const response = await axios.get(`http://localhost:8000/api/users/${userId}/keywords`)
      const keywordToDeleteId = response.data.find(k => k.word === keywordToDelete)?.id
      
      if (keywordToDeleteId) {
        await axios.delete(`http://localhost:8000/api/users/${userId}/keywords/${keywordToDeleteId}`)
        const updatedKeywords = keywords.filter(keyword => keyword !== keywordToDelete)
        setKeywords(updatedKeywords)
        onFilterChange({ use_keywords: useKeywords, keywords: updatedKeywords })
      }
    } catch (error) {
      console.error('Error al eliminar palabra clave:', error)
      setSnackbar({
        open: true,
        message: 'Error al eliminar palabra clave',
        severity: 'error'
      })
    }
  }

  const handleToggleKeywords = () => {
    const newUseKeywords = !useKeywords
    setUseKeywords(newUseKeywords)
    onFilterChange({ use_keywords: newUseKeywords, keywords })
  }

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false })
  }

  return (
    <Box>
      <Box sx={{ 
        backgroundColor: '#fff',
        borderRadius: 1,
        p: 2,
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
      }}>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            fontWeight: 'bold',
            mb: 2,
            color: '#1a1a1a'
          }}
        >
          FILTROS
        </Typography>

        <Button
          variant="contained"
          startIcon={isScrapingLoading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
          onClick={handleScrapeAll}
          disabled={isScrapingLoading}
          sx={{
            width: '100%',
            mb: 3,
            textTransform: 'none',
            backgroundColor: '#1976d2',
            '&:hover': {
              backgroundColor: '#1565c0'
            }
          }}
        >
          Actualizar Datos
        </Button>

        <Box sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              mb: 1.5, 
              fontWeight: 'bold',
              color: '#1a1a1a'
            }}
          >
            PAÍS
          </Typography>
          <ToggleButtonGroup
            value={country}
            exclusive
            onChange={handleCountryChange}
            aria-label="país"
            size="small"
            sx={{
              display: 'flex',
              width: '100%',
              '& .MuiToggleButton-root': {
                flex: 1,
                border: '1px solid #e0e0e0',
                borderRadius: '4px !important',
                mx: 0.5,
                py: 0.75,
                fontSize: '0.75rem',
                color: '#666',
                '&:first-of-type': {
                  ml: 0,
                },
                '&:last-of-type': {
                  mr: 0,
                },
                '&.Mui-selected': {
                  backgroundColor: '#1976d2',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: '#1565c0',
                  }
                }
              }
            }}
          >
            <ToggleButton value="" aria-label="todos">
              TODOS
            </ToggleButton>
            <ToggleButton value="Chile" aria-label="chile">
              CHILE
            </ToggleButton>
            <ToggleButton value="Perú" aria-label="perú">
              PERÚ
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              mb: 1.5, 
              fontWeight: 'bold',
              color: '#1a1a1a'
            }}
          >
            FUENTES
          </Typography>
          <FormControl fullWidth size="small">
            <Select
              multiple
              value={selectedSources}
              onChange={handleSourceChange}
              input={<OutlinedInput />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value.id} label={value.name} size="small" />
                  ))}
                </Box>
              )}
              sx={{ minHeight: 40 }}
            >
              {sources.map((source) => (
                <MenuItem key={source.id} value={source}>
                  {source.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              mb: 1.5, 
              fontWeight: 'bold',
              color: '#1a1a1a'
            }}
          >
            FECHA DE PRESENTACIÓN
          </Typography>
          <Stack direction="row" spacing={2}>
            <DatePicker
              label="Desde"
              value={filters.startDate || null}
              onChange={(newValue) => onFilterChange({ startDate: newValue })}
              slotProps={{
                textField: {
                  size: "small",
                  fullWidth: true,
                  InputProps: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <CalendarTodayIcon />
                      </InputAdornment>
                    ),
                  }
                }
              }}
            />
            <DatePicker
              label="Hasta"
              value={filters.endDate || null}
              onChange={(newValue) => onFilterChange({ endDate: newValue })}
              slotProps={{
                textField: {
                  size: "small",
                  fullWidth: true,
                  InputProps: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <CalendarTodayIcon />
                      </InputAdornment>
                    ),
                  }
                }
              }}
            />
          </Stack>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
            <Typography 
              variant="subtitle2" 
              sx={{ 
                fontWeight: 'bold',
                color: '#1a1a1a',
                flex: 1
              }}
            >
              PALABRAS CLAVE
            </Typography>
            <Button
              size="small"
              onClick={handleToggleKeywords}
              sx={{ 
                textTransform: 'none',
                minWidth: 'auto'
              }}
            >
              {useKeywords ? 'Desactivar' : 'Activar'}
            </Button>
          </Box>

          <Stack spacing={1}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                size="small"
                placeholder="Agregar palabra clave..."
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                fullWidth
                disabled={!useKeywords}
              />
              <Button
                variant="outlined"
                onClick={handleAddKeyword}
                disabled={!useKeywords || !newKeyword.trim()}
                sx={{ minWidth: 'auto', px: 2 }}
              >
                +
              </Button>
            </Box>

            {isLoadingKeywords ? (
              <CircularProgress size={20} sx={{ alignSelf: 'center' }} />
            ) : (
              <Box sx={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: 1,
                opacity: useKeywords ? 1 : 0.5
              }}>
                {keywords.map((keyword) => (
                  <Chip
                    key={keyword}
                    label={keyword}
                    onDelete={() => handleDeleteKeyword(keyword)}
                    disabled={!useKeywords}
                    size="small"
                  />
                ))}
              </Box>
            )}
          </Stack>
        </Box>

        <Snackbar 
          open={snackbar.open} 
          autoHideDuration={6000} 
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseSnackbar} 
            severity={snackbar.severity}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </Box>
  )
}

export default FilterPanel
