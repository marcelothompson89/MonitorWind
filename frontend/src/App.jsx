import { useState } from 'react'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { createTheme } from '@mui/material/styles'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import ItemList from './components/ItemList'
import FilterPanel from './components/FilterPanel'
import { Container, Box, Button, TextField, InputAdornment, Typography } from '@mui/material'
import LogoutIcon from '@mui/icons-material/Logout'
import SearchIcon from '@mui/icons-material/Search'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
        },
      },
    },
  },
})

function App() {
  const [filters, setFilters] = useState({
    search: '',
    country: '',
    startDate: null,
    endDate: null,
    source_type: '',
    use_keywords: false,
    keywords: []
  })
  const [totalItems, setTotalItems] = useState(0)

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters })
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Box sx={{ 
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}>
          <Container 
            maxWidth={false}
            sx={{ 
              maxWidth: '1400px',
              pt: 2,
              pb: 6
            }}
          >
            {/* Botón de cerrar sesión */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'flex-end', 
              mb: 3
            }}>
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<LogoutIcon />}
                sx={{ 
                  borderRadius: '20px',
                  fontSize: '0.875rem',
                  textTransform: 'none',
                  borderColor: '#ef5350',
                  color: '#ef5350',
                  '&:hover': {
                    borderColor: '#d32f2f',
                    backgroundColor: 'rgba(239, 83, 80, 0.04)',
                  }
                }}
              >
                Cerrar Sesión
              </Button>
            </Box>

            {/* Barra de búsqueda y contador */}
            <Box sx={{ 
              display: 'flex',
              gap: { xs: 0, md: 3 },
              flexDirection: { xs: 'column', md: 'row' }
            }}>
              <Box sx={{ 
                width: { xs: '100%', md: '280px' },
                flexShrink: 0,
                backgroundColor: 'white',
                p: 3,
                borderRadius: 2,
                boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
                mb: { xs: 3, md: 0 }
              }}>
                <FilterPanel 
                  filters={filters} 
                  onFilterChange={handleFilterChange}
                />
              </Box>
              
              <Box sx={{ flexGrow: 1 }}>
                <Box sx={{ mb: 3 }}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Buscar por título, descripción o país"
                    variant="outlined"
                    value={filters.search}
                    onChange={(e) => handleFilterChange({ search: e.target.value })}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon sx={{ color: '#9e9e9e' }} />
                        </InputAdornment>
                      ),
                      sx: {
                        backgroundColor: 'white',
                        borderRadius: '8px',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#e0e0e0',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#bdbdbd',
                        },
                        '& input': {
                          fontSize: '0.875rem',
                          padding: '8px 0',
                        }
                      }
                    }}
                  />
                  {totalItems > 0 && (
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        mt: 1, 
                        color: 'text.secondary',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5
                      }}
                    >
                      <strong>{totalItems}</strong> {totalItems === 1 ? 'registro encontrado' : 'registros encontrados'}
                    </Typography>
                  )}
                </Box>
                <ItemList 
                  filters={filters} 
                  onTotalItemsChange={setTotalItems}
                />
              </Box>
            </Box>
          </Container>
        </Box>
      </LocalizationProvider>
    </ThemeProvider>
  )
}

export default App
