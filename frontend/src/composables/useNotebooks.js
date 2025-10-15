import { ref } from 'vue'

export function useNotebooks() {
  const notebooks = ref([
    {
      id: '1',
      title: 'Análise Facebook Ads - Setembro',
      description: 'Análise de performance das campanhas do Facebook',
      createdAt: '2024-10-10',
      filesCount: 2,
      lastInsight: 'CPC médio aumentou 15% na última semana',
    },
    {
      id: '2',
      title: 'Google Ads Q3',
      description: 'Performance trimestral do Google Ads',
      createdAt: '2024-10-08',
      filesCount: 3,
      lastInsight: 'ROAS melhorou em 23% comparado ao Q2',
    },
    {
      id: '3',
      title: 'Comparativo Multi-canal',
      description: 'Análise comparativa entre Facebook e Google',
      createdAt: '2024-10-05',
      filesCount: 5,
      lastInsight: 'Facebook tem melhor CTR, Google melhor taxa de conversão',
    },
  ])

  const createNotebook = (title, description) => {
    const newNotebook = {
      id: Date.now().toString(),
      title,
      description,
      createdAt: new Date().toISOString().split('T')[0],
      filesCount: 0,
      lastInsight: 'Aguardando upload de dados',
    }
    notebooks.value.unshift(newNotebook)
    return newNotebook
  }

  const deleteNotebook = (id) => {
    const index = notebooks.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notebooks.value.splice(index, 1)
    }
  }

  const getNotebook = (id) => {
    return notebooks.value.find(n => n.id === id)
  }

  return {
    notebooks,
    createNotebook,
    deleteNotebook,
    getNotebook,
  }
}
