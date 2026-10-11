import { computed, reactive, ref, watch } from 'vue'

export const PAGE_SIZE = 20

/**
 * Search / filter / sort / paginate a server-side document list.
 * Stale responses are discarded so an older request cannot overwrite newer results.
 */
export function useDocumentList(api) {
  const items = ref([])
  const count = ref(0)
  const loading = ref(false)
  const error = ref('')
  const query = reactive({ search: '', template: '', ordering: '-updated_at', page: 1 })
  let requestSeq = 0
  let debounce = null

  async function load() {
    const seq = ++requestSeq
    loading.value = true
    error.value = ''
    try {
      const data = await api.list({
        search: query.search.trim(),
        template: query.template,
        ordering: query.ordering,
        page: query.page,
      })
      if (seq !== requestSeq) return
      items.value = data.results
      count.value = data.count
    } catch (err) {
      if (seq === requestSeq) error.value = err.message
    } finally {
      if (seq === requestSeq) loading.value = false
    }
  }

  watch(
    () => query.search,
    () => {
      clearTimeout(debounce)
      debounce = setTimeout(() => {
        query.page = 1
        load()
      }, 300)
    },
  )
  watch(
    () => [query.template, query.ordering],
    () => {
      query.page = 1
      load()
    },
  )
  watch(
    () => query.page,
    () => load(),
  )

  const totalPages = computed(() => Math.max(1, Math.ceil(count.value / PAGE_SIZE)))
  const hasPrev = computed(() => query.page > 1)
  const hasNext = computed(() => query.page < totalPages.value)

  return { items, count, loading, error, query, load, totalPages, hasPrev, hasNext }
}
