import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { mockVisitors } from '../../data/mockVisitor'
import styles from './index.module.scss'

export default function VisitorListPage() {
  const goAdd = () => Taro.navigateTo({ url: '/pages/visitor-add/index' })
  const goDetail = (id: number) => Taro.navigateTo({ url: `/pages/visitor-detail/index?id=${id}` })
  const goLeave = (id: number) => Taro.showToast({ title: `访客 #${id} 已标记离场`, icon: 'success' })

  return (
    <View className={styles.page}>
      <View className={styles.header}>
        <Text className={styles.title}>访客登记中心</Text>
        <Text className={styles.addBtn} onClick={goAdd}>+ 新增登记</Text>
      </View>

      <View className={styles.filters}>
        <Text className={styles.filterText}>支持按来访日期、拜访业主、在访/已离场状态筛选</Text>
      </View>

      {mockVisitors.map((visitor) => (
        <View key={visitor.id} className={styles.item}>
          <View className={styles.itemHeader}>
            <Text className={styles.name}>{visitor.name}</Text>
            <Text className={visitor.status === 'visiting' ? styles.statusActive : styles.statusLeft}>
              {visitor.status === 'visiting' ? '在访' : '已离场'}
            </Text>
          </View>
          <Text className={styles.meta}>拜访业主：{visitor.ownerName}</Text>
          <Text className={styles.meta}>关联房号：{visitor.unitName}</Text>
          <Text className={styles.meta}>来访事由：{visitor.visitReason}</Text>
          <Text className={styles.meta}>登记时间：{visitor.registerTime}</Text>
          <View className={styles.actions}>
            <Text className={styles.detailBtn} onClick={() => goDetail(visitor.id)}>详情</Text>
            {visitor.status === 'visiting' && (
              <Text className={styles.leaveBtn} onClick={() => goLeave(visitor.id)}>标记离场</Text>
            )}
          </View>
        </View>
      ))}

      {mockVisitors.length === 0 && <Text className={styles.empty}>暂无访客记录</Text>}
    </View>
  )
}
