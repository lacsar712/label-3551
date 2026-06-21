import { View, Text } from '@tarojs/components'
import type { Visitor } from '../../types/visitor'
import styles from './index.module.scss'

interface Props {
  visitor: Visitor
  onDetail?: (id: number) => void
}

export default function VisitorCard({ visitor, onDetail }: Props) {
  return (
    <View className={styles.card} onClick={() => onDetail?.(visitor.id)}>
      <View className={styles.header}>
        <Text className={styles.name}>{visitor.name}</Text>
        <Text className={visitor.status === 'visiting' ? styles.badgeActive : styles.badgeLeft}>
          {visitor.status === 'visiting' ? '在访' : '已离场'}
        </Text>
      </View>
      <Text className={styles.reason}>来访事由：{visitor.visitReason}</Text>
      <Text className={styles.meta}>到访房号：{visitor.unitName}</Text>
      <Text className={styles.meta}>登记时间：{visitor.registerTime}</Text>
    </View>
  )
}
