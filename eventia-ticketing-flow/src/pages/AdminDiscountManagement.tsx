import React from 'react';
import AdminLayout from '@/components/layout/AdminLayout';
import { DiscountManagement } from '@/components/DiscountManagement';
import { Helmet } from 'react-helmet-async';

const AdminDiscountManagement = () => {
  return (
    <AdminLayout>
      <Helmet>
        <title>Discount Management | Eventia Admin</title>
      </Helmet>
      <DiscountManagement />
    </AdminLayout>
  );
};

export default AdminDiscountManagement;
